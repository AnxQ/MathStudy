from CUMCM2018.machine import CNC, RGV, Workpiece, CNCType
from typing import List
import xlwt

# 当前可行最优解
initialList = [1, 5, 2, 6, 3, 7, 4, 8, 9, 13, 10, 14, 11, 15, 12, 16]

rgv = RGV(position=0,
          up_time_1=28,
          up_time_2=31,
          wash_time=25,
          move_time=[0, 20, 33, 46])
cnc_raid: List[CNC] = [CNC(single_produce_time=560, identity=2 * i + 1, far=False, position=i, maintance=True) for i in range(0, 4)] + \
                      [CNC(single_produce_time=560, identity=2 * i + 2, far=True, position=i, maintance=True) for i in range(0, 4)]


def simulate(initial_plan, output=False):
    workpieces = []

    # 重置RGV CNC
    rgv.reset()
    for cnc in cnc_raid:
        cnc.reset()

    idle_cnc = filter(lambda x: x.finish_tick <= tick, cnc_raid)

    tick = 0
    max_tick = 8 * 3600

    # 若不允许预测CNC完成时间则将评价修正为此算法
    def evaluate_idle(current_tick) -> CNC:
        idle_cnc = filter(lambda x: x.finish_tick <= tick, cnc_raid)
        return min(idle_cnc,
                   key=lambda x: max(rgv.move_time[abs(x.position - rgv.position)], x.finish_tick - current_tick) +
                                 (rgv.up_time_2 if x.far else rgv.up_time_1))

    # 按照当前时间成本最短来寻找一个最优化CNC并提前前往
    def evaluate_overall(current_tick) -> CNC:
        return min(cnc_raid,
                   key=lambda x: max(rgv.move_time[abs(x.position - rgv.position)], x.finish_tick - current_tick) +
                                 (rgv.up_time_2 if x.far else rgv.up_time_1))

    i = 1
    while tick < max_tick:
        # 首次执行，按照给定初始方案执行
        if i < 16:
            chosen_cnc = cnc_raid[(initial_plan[i - 1] - 1) % 8]
        # 随后进行事件驱动调度
        # 评估后挑选一个最优的CNC进行动作
        else:
            chosen_cnc = evaluate_overall(tick)
        new_wp = Workpiece(identity=i)
        workpieces.append(new_wp)
        tick = rgv.move(chosen_cnc, tick)
        tick = rgv.up(new_wp, chosen_cnc, tick)
        # 当RGV仅仅等待指令时，重置系统时间点为cnc的完成时间
        # 此时启用以下代码
        # tick = max(min(map(lambda x: x.finish_tick, cnc_raid)), rgv.finish_tick)
        i += 1

    workpieces_fin = list(filter(lambda x: x.down_tick and not x.status == CNCType.Abandon, workpieces))
    workpieces_abd = list(filter(lambda x: x.status == CNCType.Abandon, workpieces))

    if output:
        book = xlwt.Workbook(encoding='utf-8')
        sheet: xlwt.Worksheet = book.add_sheet('Simulation_Result')
        for i, wp in enumerate(workpieces_fin):
            sheet.write(i, 0, wp.identity)
            sheet.write(i, 1, wp.mother_cnc.identity)
            sheet.write(i, 2, wp.up_tick)
            sheet.write(i, 3, wp.down_tick)

        sheet: xlwt.Worksheet = book.add_sheet('Simulation_Result_Failure')
        for i, wp in enumerate(workpieces_abd):
            sheet.write(i, 0, wp.identity)
            sheet.write(i, 1, wp.mother_cnc.identity)
            sheet.write(i, 2, wp.error_tick)
            sheet.write(i, 3, wp.recovery_tick)

        book.save('Condition3_TS_G1.xls')

    return workpieces_fin.__len__()


def taboo_search():
    taboo_loops = 0
    tabooList = []
    currentList = initialList
    initialBest = (initialList, simulate(initialList))
    BestList = [initialBest]
    while taboo_loops < 6000:
        # 取得临域空间
        swaplistList = []
        for i in range(0, len(currentList) - 1):
            swap_pair = currentList[i:i + 2]
            if tuple(swap_pair) not in tabooList:
                swaped_list = currentList[:i] + swap_pair[::-1] + currentList[i + 2:]
                swaplistList.append((
                    swaped_list,
                    simulate(swaped_list),
                    tuple(swap_pair)
                ))
        if not len(swaplistList):
            if len(tabooList) < 240:
                # 此时判定方案被阻塞，应释放当前存在于队列里的所有禁忌
                # 为避免出现循环，记录此刻的currentList
                # 如果之前出现过当前序列
                for i in range(0, len(currentList) - 1):
                    tabooList.remove(tuple(currentList[i:i + 2]))
                continue
            else:
                break
        currentBest = min(swaplistList, key=lambda x: x[1])
        currentList = currentBest[0]
        if currentBest[1] > initialBest[1]:
            BestList.append(currentBest)
        tabooList.append(currentBest[2])
        taboo_loops += 1
    if taboo_loops >= 6000:
        print("Reached the looping limit.")
    return BestList


if __name__ == "__main__":
    # print(taboo_search())
    simulate([1, 5, 2, 6, 3, 7, 4, 8, 9, 13, 10, 14, 11, 15, 12, 16], output=True)
