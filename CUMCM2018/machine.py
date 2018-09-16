from enum import Enum
import numpy as np

debug_mode = False


class Workpiece:
    def __init__(self, **kwargs):
        self.up_tick = 0
        self.down_tick = 0
        self.mother_cnc = None

        self.up_tick_1 = 0
        self.up_tick_2 = 0
        self.down_tick_1 = 0
        self.down_tick_2 = 0
        self.mother_cnc_1 = None
        self.mother_cnc_2 = None

        self.identity = 0
        self.status = CNCType.S

        self.error_tick = 0
        self.recovery_tick = 0
        for k, v in kwargs.items():
            setattr(self, k, v)
        return

    def __str__(self):
        return f"{self.mother_cnc.identity}"


class MachineBase:
    def __init__(self):
        self.finish_tick = 0


class CNCType(Enum):
    Abandon = -1
    S = 0
    A = 1
    B = 2


class CNC(MachineBase):
    def __init__(self, **kwargs):
        self.single_produce_time = 0
        self.step_1_produce_time = 0
        self.step_2_produce_time = 0
        self.position = 0
        self.identity = 0
        self.type = CNCType.S
        self.working_workpiece = None
        self.far = False
        self.maintance = False
        for k, v in kwargs.items():
            setattr(self, k, v)
        MachineBase.__init__(self)
        return

    def reset(self):
        self.finish_tick = 0
        self.working_workpiece = None

    def process(self, workpiece: Workpiece, current_tick):
        # 有可能故障
        if self.maintance:
            # 此时判定是否出现故障
            if np.random.rand() < 0.01:
                workpiece.status = CNCType.Abandon
                workpiece.mother_cnc = self
                workpiece.error_tick = current_tick + (self.single_produce_time if workpiece.status == CNCType.S else
                                                       self.step_1_produce_time if workpiece.status == CNCType.A else
                                                       self.step_2_produce_time) * np.random.rand()
                workpiece.recovery_tick = workpiece.error_tick + 600 + np.random.rand() * 600
                self.finish_tick = workpiece.recovery_tick
                temp = self.working_workpiece
                self.working_workpiece = None
                return temp
        if workpiece.status == CNCType.S:
            if debug_mode:
                print(f"{current_tick}: CNC{self.identity} Process WP{workpiece.identity} start.")
            workpiece.mother_cnc = self
            self.working_workpiece = workpiece
            self.finish_tick = current_tick + self.single_produce_time
            return
        elif workpiece.status == CNCType.A:
            return self.process_step_1(workpiece, current_tick)
        else:
            return self.process_step_2(workpiece, current_tick)

    def process_step_1(self, workpiece, current_tick):
        if debug_mode:
            print(f"{current_tick}: CNC {self.type.name}{self.identity} Process {workpiece.identity} start.")
        workpiece.mother_cnc_1 = self
        temp = self.working_workpiece
        self.working_workpiece = workpiece
        self.finish_tick = current_tick + self.step_1_produce_time
        return temp

    def process_step_2(self, workpiece, current_tick):
        if debug_mode:
            print(f"{current_tick}: CNC {self.type.name}{self.identity} Process {workpiece.identity} start.")
        workpiece.mother_cnc_2 = self
        temp = self.working_workpiece
        self.working_workpiece = workpiece
        self.finish_tick = current_tick + self.step_2_produce_time
        return temp


class RGV(MachineBase):
    def __init__(self, **kwargs):
        self.wash_time = 0
        self.up_time_1 = 0
        self.up_time_2 = 0
        self.move_time = []
        self.position = 0
        self.holding_workpiece = None
        self.washing_workpiece = None
        for k, v in kwargs.items():
            setattr(self, k, v)
        MachineBase.__init__(self)
        return

    def reset(self):
        self.position = 0
        self.holding_workpiece = None
        self.washing_workpiece = None
        self.finish_tick = None
        pass

    def wash(self, workpiece: Workpiece, current_tick):
        if debug_mode:
            print(
                f"{current_tick}: Wash WP {workpiece.identity}, Remove {self.washing_workpiece.identity if self.washing_workpiece else ''}")
        self.finish_tick = current_tick + self.wash_time
        self.washing_workpiece = workpiece
        return

    def up(self, workpiece: Workpiece, cnc: CNC, current_tick):
        # 若当前CNC尚未完成，则选择等待上料
        if cnc.finish_tick > current_tick:
            if debug_mode:
                print(f"{current_tick}: Wait for CNC{cnc.identity} {cnc.finish_tick - current_tick}s")
            current_tick = cnc.finish_tick

        # 上料
        if debug_mode:
            print(f"{current_tick}: Upload WP{workpiece.identity} -> CNC{cnc.identity}")
        self.finish_tick = current_tick + (self.up_time_2 if cnc.far else self.up_time_1)

        # 单加工过程
        if workpiece.status == CNCType.S:
            workpiece.up_tick = current_tick
            # 如果当前CNC上已经"有料"，则进行清洗操作
            # 该过程开始执行与开始加工同步
            if cnc.working_workpiece:
                cnc.working_workpiece.down_tick = current_tick
                current_tick = self.finish_tick
                self.wash(cnc.working_workpiece, current_tick)
            current_tick = self.finish_tick
            cnc.process(workpiece, current_tick)

        # 多步加工 A (下B料上A料)
        elif workpiece.status == CNCType.A:
            if not cnc.type == CNCType.A:
                return None
            workpiece.up_tick_1 = current_tick

            self.holding_workpiece = cnc.process(workpiece, self.finish_tick)
            if self.holding_workpiece:
                self.holding_workpiece.status = CNCType.B
                self.holding_workpiece.down_tick_1 = current_tick

        # 多步加工 B（下成料上B料并清洗）
        else:
            if not cnc.type == CNCType.B:
                return None
            workpiece.up_tick_2 = current_tick

            self.holding_workpiece = cnc.process(workpiece, self.finish_tick)
            # 换料后执行清洗
            if self.holding_workpiece:
                self.holding_workpiece.down_tick_2 = current_tick
                current_tick = self.finish_tick
                self.wash(self.holding_workpiece, current_tick)

        return self.finish_tick

    def move(self, cnc: CNC, current_tick):
        # 移动
        if debug_mode:
            print(f"{current_tick}: Move to CNC {cnc.identity}")
        current_move_time = self.move_time[abs(self.position - cnc.position)]
        self.position = cnc.position
        self.finish_tick = current_tick + current_move_time
        current_tick = self.finish_tick
        return current_tick
