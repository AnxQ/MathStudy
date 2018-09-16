from CUMCM2018.machine import CNC, RGV, Workpiece, CNCType, debug_mode
from typing import List, Tuple
import xlwt

max_tick = 8 * 3600

initialList = [CNCType.A,
               CNCType.A,
               CNCType.A,
               CNCType.A,
               CNCType.B,
               CNCType.B,
               CNCType.B,
               CNCType.B]


def simulate(cnc_type_ref, output=False):
    tick = 0
    i = 1
    workpieces = []
    rgv = RGV(position=0,
              up_time_1=30,
              up_time_2=35,
              wash_time=30,
              move_time=[0, 23, 41, 59])

    cnc_raid: List[CNC] = [CNC(step_1_produce_time=280, step_2_produce_time=500, identity=2 * i + 1,
                               far=False, position=i) for i in range(0, 4)] + \
                          [CNC(step_1_produce_time=280, step_2_produce_time=500, identity=2 * i + 2,
                               far=True, position=i) for i in range(0, 4)]

    for cnc_naked in cnc_raid:
        cnc_naked.type = cnc_type_ref[cnc_raid.index(cnc_naked)]

    cnc_A = list(filter(lambda x: x.type == CNCType.A, cnc_raid))
    cnc_B = list(filter(lambda x: x.type == CNCType.B, cnc_raid))

    possible_result = []

    for ca in cnc_A:
        for cb in cnc_B:
            possible_result.append((ca, cb))

    def evaluate_pair(current_tick) -> Tuple[CNC, CNC]:
        # 寻找一个最好的机器对以提前动身

        # 优先寻找空闲 A
        idle_A = list(filter(lambda x: x.finish_tick <= current_tick, cnc_A))
        if len(idle_A):
            idle_A = min(idle_A, key=lambda x: abs(x.position - rgv.position))
            return (idle_A, min(cnc_B,
                                key=lambda x: max(rgv.move_time[abs(x.position - idle_A.position)],
                                                  x.finish_tick - current_tick)))

        def time_cost(pair: Tuple[CNC, CNC]):
            # 若果CNC完成时间差小于 UP+MOVE
            # if pair[1].finish_tick > pair[0].finish_tick:
            #     return

            # 即 R-A-B 的移动时间+等待时间最短
            return \
                max(rgv.move_time[abs(pair[0].position - rgv.position)], pair[0].finish_tick - current_tick) + \
                max(rgv.move_time[abs(pair[1].position - pair[0].position)] + (rgv.up_time_2 if pair[0].far else rgv.up_time_1),
                pair[1].finish_tick - pair[0].finish_tick) + (rgv.up_time_2 if pair[1].far else rgv.up_time_1)

        chosen_pair = min(possible_result, key=lambda x: time_cost(x))
        # print(chosen_pair, time_cost(chosen_pair))
        return chosen_pair

    while tick < max_tick:
        chosen_A_B = evaluate_pair(tick)
        new_wp = Workpiece(identity=i, status=CNCType.A)
        workpieces.append(new_wp)
        # 完成一个连贯的动作 A-B
        tick = rgv.move(chosen_A_B[0], tick)
        tick = rgv.up(new_wp, chosen_A_B[0], tick)
        # 若卸下来工件则携带工件前往 B
        if rgv.holding_workpiece is not None:
            tick = rgv.move(chosen_A_B[1], tick)
            tick = rgv.up(rgv.holding_workpiece, chosen_A_B[1], tick)
        # 重置时间为任意一台A最早完成的时间，但是不能早于RGV当前的完成时间
        # tick = max(min(map(lambda x: x.finish_tick, cnc_A)), rgv.finish_tick)
        i += 1

    workpieces_fin = list(filter(lambda x: x.down_tick_2, workpieces))
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
        book.save('Condition2_VS_G2.xls')

    return workpieces.__len__()


def violence_search():
    entire_list = []
    for i in range(0, 256):
        currentList = [CNCType(int(c) + 1) for c in f"{bin(i).replace('0b',''):0>8}"]
        if not currentList.count(CNCType(1)) == 0 and not currentList.count(CNCType(2)) == 0:
            entire_list.append(currentList)
    return max(entire_list, key=lambda x: simulate(x))


result = violence_search()

simulate(result, output=True)
