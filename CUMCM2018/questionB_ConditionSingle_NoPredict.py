"""
当不允许提前移动RGV的情况下，使用该算法进行整体分配
"""
from CUMCM2018.machine import CNC, RGV, Workpiece
from typing import List

workpieces = []

# 初始化RGV对象
rgv = RGV(
    position=0,    # RGV初始位置
    up_time_1=28,  # RGV给1、3、5、7上料的时间
    up_time_2=31,  # RGV给2、4、6、8上料的时间
    wash_time=25,  # RGV清洗时间
    move_time=[0, 20, 33, 46]  # RGV移动0、1、2、3路程所需时间
)

# 初始化CNC工作阵列
#                          单个产品时间               CNC序号             CNC处于上料侧还是下料侧 CNC坐标，用于距离计算
cnc_raid: List[CNC] = [CNC(single_produce_time=560, identity=2 * i + 1, far=False, position=i) for i in range(0, 4)] + \
                      [CNC(single_produce_time=560, identity=2 * i + 2, far=True, position=i) for i in range(0, 4)]

idle_cnc = filter(lambda x: x.finish_tick <= tick, cnc_raid)

tick = 0
max_tick = 8 * 3600


def evaluate_idle(current_tick) -> CNC:
    idle_cnc = filter(lambda x: x.finish_tick <= tick, cnc_raid)
    return min(idle_cnc,
               key=lambda x: max(rgv.move_time[abs(x.position - rgv.position)], x.finish_tick - current_tick) +
                             (rgv.up_time_2 if x.far else rgv.up_time_1))

i = 1
while tick < max_tick:
    # 事件驱动调度
    # 评估后挑选一个最优的CNC进行动作
    chosen_cnc = evaluate_idle(tick)

    # 产生新的生料
    new_wp = Workpiece(identity=i)
    workpieces.append(new_wp)
    tick = rgv.move(chosen_cnc, tick)
    tick = rgv.up(new_wp, chosen_cnc, tick)

    # 重置当前
    tick = max(min(map(lambda x: x.finish_tick, cnc_raid)), rgv.finish_tick)
    i += 1

print(workpieces.__len__())
