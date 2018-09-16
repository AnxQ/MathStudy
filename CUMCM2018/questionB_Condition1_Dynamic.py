from CUMCM2018.machine import CNC, RGV, Workpiece
from typing import List

workpieces = []
rgv = RGV(position=0,
          up_time_1=28,
          up_time_2=31,
          wash_time=25,
          move_time=[0, 20, 33, 46])
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


def evaluate_overall(current_tick) -> CNC:
    # 寻找一个最好CNC并提前前往
    return min(cnc_raid,
               key=lambda x: max(rgv.move_time[abs(x.position - rgv.position)], x.finish_tick - current_tick) +
                             (rgv.up_time_2 if x.far else rgv.up_time_1))


i = 1
while tick < max_tick:
    # 事件驱动调度
    # 评估后挑选一个最优的CNC进行动作
    chosen_cnc = evaluate_idle(tick)
    new_wp = Workpiece(identity=i)
    workpieces.append(new_wp)
    tick = rgv.move(chosen_cnc, tick)
    tick = rgv.up(new_wp, chosen_cnc, tick)
    tick = max(min(map(lambda x: x.finish_tick, cnc_raid)), rgv.finish_tick)
    i += 1

print(workpieces.__len__())
# 此时执行收尾工作
