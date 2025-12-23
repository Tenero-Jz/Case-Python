
class DMMotorDrive(object):
    def __init__(self, port):
        pass

    def power_on(self, joint_id: int):
        pass

    def power_off(self, joint_id: int):
        pass

    def power_on_all(self):
        pass

    def power_off_all(self):
        pass

    def set_joint_calibration(self, joint_id: int):
        pass

    def send_angle(self, joint_id: int, angle: float, speed: int):
        pass

    def send_angles(self, angles: list, speeds: int):
        pass

    def get_angles(self):
        pass

    def get_angle(self, joint_id: int):
        pass

    def clear_error(self, joint_id: int):
        pass

    def get_error_status(self, joints: list):
        pass

    def gripper_control(self, mode: int):
        pass


class SD100(object):
    def __init__(self, port):
        pass

    def power_on(self):
        pass

    def set_pos(self, _id: int,  len: int, speed: int = 100, acc: int = 200, dec: int = 200):
        pass

    def set_mode(self, mode: int):
        pass

    def set_speed(self, speed: int):
        pass

    def set_acc(self, acc: int):
        pass

    def set_dec(self, dec: int):
        pass

    def read_pos(self, _id: int):
        pass

    def run(self, _id: int):
        pass

    def stop(self, _id: int):
        pass
