from CUMCM2018.machine import CNC, RGV, Workpiece, CNCType, debug_mode
from typing import List, Tuple
import xlwt
from datetime import datetime

max_tick = 8 * 3600

def simulate(cnc_type_ref, output=False, filename=f"output_{datetime.now().strftime('%b%d%Y_%H%M%S')}.xls", cnc_fail=False):
    tick = 0
    i = 1
    workpieces = []

    # 属性含义同前
    rgv = RGV(position=0,
              up_time_1=27,
              up_time_2=32,
              wash_time=25,
              move_time=[0, 18, 32, 46])

    # 初始化CNC                 第一步加工时间             第二步加工时间             (其他属性同前)
    cnc_raid: List[CNC] = [CNC(step_1_produce_time=455, step_2_produce_time=182, identity=2 * i + 1, maintance=cnc_fail,
                               far=False, position=i) for i in range(0, 4)] + \
                          [CNC(step_1_produce_time=455, step_2_produce_time=182, identity=2 * i + 2, maintance=cnc_fail,
                               far=True, position=i) for i in range(0, 4)]

    for cnc_naked in cnc_raid:
        cnc_naked.type = cnc_type_ref[cnc_raid.index(cnc_naked)]

    cnc_A = list(filter(lambda x: x.type == CNCType.A, cnc_raid))
    cnc_B = list(filter(lambda x: x.type == CNCType.B, cnc_raid))

    possible_result = []

    for ca in cnc_A:
        for cb in cnc_B:
            possible_result.append((ca, cb))

    def evaluate_a(current_tick) -> CNC:
        return min(cnc_A,
                   key=lambda x: max(rgv.move_time[abs(x.position - rgv.position)], x.finish_tick - current_tick) +
                                 (rgv.up_time_2 if x.far else rgv.up_time_1))

    def evaluate_b(current_tick) -> CNC:
        return min(cnc_B,
                   key=lambda x: max(rgv.move_time[abs(x.position - rgv.position)], x.finish_tick - current_tick) +
                                 (rgv.up_time_2 if x.far else rgv.up_time_1))

    while tick < max_tick:
        chosen_a = evaluate_a(tick)
        new_wp = Workpiece(identity=i, status=CNCType.A)
        workpieces.append(new_wp)
        # 完成一个连贯的动作 A-B
        tick = rgv.move(chosen_a, tick)
        tick = rgv.up(new_wp, chosen_a, tick)
        # 若卸下来工件则携带工件前往 B
        if rgv.holding_workpiece is not None:
            chosen_b = evaluate_b(tick)
            tick = rgv.move(chosen_b, tick)
            tick = rgv.up(rgv.holding_workpiece, chosen_b, tick)
        # 重置时间为任意一台A最早完成的时间，但是不能早于RGV当前的完成时间
        # tick = max(min(map(lambda x: x.finish_tick, cnc_A)), rgv.finish_tick)
        i += 1

    workpieces_fin = list(filter(lambda x: x.down_tick_2 and not x.status == CNCType.Abandon, workpieces))
    workpieces_abd = list(filter(lambda x: x.status == CNCType.Abandon, workpieces))

    # 用于输出Excel文档
    if output:
        book = xlwt.Workbook(encoding='utf-8')
        sheet: xlwt.Worksheet = book.add_sheet('Simulation_Result')
        for i, wp in enumerate(workpieces_fin):
            sheet.write(i, 0, wp.identity)
            sheet.write(i, 1, wp.mother_cnc_1.identity)
            sheet.write(i, 2, wp.up_tick_1)
            sheet.write(i, 3, wp.down_tick_1)
            sheet.write(i, 4, wp.mother_cnc_2.identity)
            sheet.write(i, 5, wp.up_tick_2)
            sheet.write(i, 6, wp.down_tick_2)
        sheet: xlwt.Worksheet = book.add_sheet('Simulation_Result_Failure')
        for i, wp in enumerate(workpieces_abd):
            sheet.write(i, 0, wp.identity)
            sheet.write(i, 1, wp.mother_cnc.identity)
            sheet.write(i, 2, wp.error_tick)
            sheet.write(i, 3, wp.recovery_tick)
        book.save(filename)
    return workpieces.__len__()


def violence_search():
    """
    暴力搜索算法
    :return: 当前最优方案
    """
    entire_list = []
    for i in range(0, 256):
        currentList = [CNCType(int(c) + 1) for c in f"{bin(i).replace('0b',''):0>8}"]
        if not currentList.count(CNCType(1)) == 0 and not currentList.count(CNCType(2)) == 0:
            entire_list.append(currentList)
    return max(entire_list, key=lambda x: simulate(x))


if __name__ == "__main__":
    # 由于刀片加装方案数量少(<256种)，可以通过暴搜得出最优的方案
    result = violence_search()
    print(result)

    # 将当前结果输出到Excel文档（无故障）
    simulate(result, output=True, filename="Condition2_VS_G#.xls")

    # 模拟故障，并输出一种应对序列到Excel文档
    simulate(result, output=True, filename="Condition4_VS_G#.xls", cnc_fail=True)
