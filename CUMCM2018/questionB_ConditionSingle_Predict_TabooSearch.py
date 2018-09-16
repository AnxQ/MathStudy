"""
允许对RGV的下一个目标进行预测，使用该算法进行最优解的搜索及结果的生成
将CNC对象的maintance属性设置为True以模拟故障情况
"""
from CUMCM2018.machine import CNC, RGV, Workpiece, CNCType
from typing import List
from datetime import datetime
import xlwt

# 当前可行最优解，即禁忌搜索的初始状态
initialList = [1, 5, 2, 6, 3, 7, 4, 8, 9, 13, 10, 14, 11, 15, 12, 16]

# 初始化RGV对象
rgv = RGV(
    position=0,    # RGV初始位置
    up_time_1=27,  # RGV给1、3、5、7上料的时间
    up_time_2=32,  # RGV给2、4、6、8上料的时间
    wash_time=25,  # RGV清洗时间
    move_time=[0, 18, 32, 46]   # RGV移动0、1、2、3路程所需时间
)

# 初始化CNC工作阵列
#                          单个产品时间               CNC序号             CNC处于上料侧还是下料侧
cnc_raid: List[CNC] = [CNC(single_produce_time=545, identity=2 * i + 1, far=False, position=i, maintance=False) for i in range(0, 4)] + \
                      [CNC(single_produce_time=545, identity=2 * i + 2, far=True, position=i, maintance=False) for i in range(0, 4)]


def simulate(initial_plan, output=False, filename=f"output_{datetime.now().strftime('%b%d%Y_%H%M%S')}.xls"):
    """
    对整个班次进行模拟，采用滚动窗口的方式，应对一切突发情况
    :param initial_plan: 初始对CNC进行选择的队列
    :param output: 是否输出到xls文档，默认否
    :param filename: 输出文档名称
    :return: 返回当前方法模拟后的完成工件的数量
    """
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

    # 用于Excel文档的输出
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

        book.save(filename)

    return workpieces_fin.__len__()


def taboo_search():
    """
    禁忌搜索算法
    :return: 返回迭代完成后的优于初始解的解集
    """
    taboo_loops = 0
    tabooList = []
    currentList = initialList
    initialBest = (initialList, simulate(initialList))
    BestList = [initialBest]
    while taboo_loops < 2000:
        # 取得邻域空间
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
                # 此时判定方案被阻塞，应释放存在于当前队列里的所有禁忌，以增加交换深度
                for i in range(0, len(currentList) - 1):
                    tabooList.remove(tuple(currentList[i:i + 2]))
                continue
            else:
                break
        currentBest = min(swaplistList, key=lambda x: x[1])
        currentList = currentBest[0]
        if currentBest[1] > initialBest[1]:
            # 若得到更优的解集，则进行记录
            BestList.append(currentBest)
        tabooList.append(currentBest[2])
        taboo_loops += 1
    if taboo_loops >= 2000:
        # 提示TS过程由于达到最大迭代深度而退出
        print("Reached the looping limit.")
    return BestList


if __name__ == "__main__":
    # 首先由禁忌搜索算法找出最优解
    result = taboo_search()
    print(result)

    # 将当前结果输出到Excel文档（无故障）
    simulate(result, output=True, filename="Condition1_TS_G#.xls")

    # 模拟故障，并输出一种应对序列到Excel文档
    for cnc in cnc_raid:
        cnc.maintance = True
    simulate(result, output=True, filename="Condition3_TS_G#.xls")
