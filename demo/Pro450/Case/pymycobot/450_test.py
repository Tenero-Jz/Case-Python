"""
450_test.py
This module controls the robotic arm movements.

Author: Wang Weijian
Date: 2025-08-20
"""
from pymycobot.robot_info import RobotLimit


class MyCobotPro450DataException(Exception):
    pass


def check_value_type(parameter, value_type, exception_class, _type):
    if value_type is not _type:
        raise exception_class(
            "The acceptable parameter {} should be an {}, but the received {}".format(parameter, _type, value_type))


def check_coords(parameter_name, value, robot_limit, class_name, exception_class, serial_port=None):
    if not isinstance(value, list):
        raise exception_class("`{}` must be a list, but the received {}".format(parameter_name, type(value)))
    if len(value) != 6:
        raise exception_class(
            "The length of `{}` must be 6, but the received length is {}".format(parameter_name, len(value)))
    if serial_port:
        if serial_port == "/dev/left_arm":
            min_coord = robot_limit[class_name]["left_coords_min"]
            max_coord = robot_limit[class_name]["left_coords_max"]
        elif serial_port == "/dev/right_arm":
            min_coord = robot_limit[class_name]["right_coords_min"]
            max_coord = robot_limit[class_name]["right_coords_max"]
    else:
        min_coord = robot_limit[class_name]["coords_min"]
        max_coord = robot_limit[class_name]["coords_max"]
    for idx, coord in enumerate(value):
        if not min_coord[idx] <= coord <= max_coord[idx]:
            raise exception_class(
                "Has invalid coord value, error on index {0}, received {3}, but coord should be {1} ~ {2}.".format(
                    idx, min_coord[idx], max_coord[idx], coord
                )
            )


def check_angles(angle_value, robot_limit, class_name, exception_class):
    # Check if angle_value is a list
    if not isinstance(angle_value, list):
        raise exception_class("`angles` must be a list, but the received {}".format(type(angle_value)))
    # Check angles
    if len(angle_value) != 6:
        raise exception_class("The length of `angles` must be 6, but received length is {}".format(len(angle_value)))
    for idx, angle in enumerate(angle_value):
        if not robot_limit[class_name]["angles_min"][idx] <= angle <= robot_limit[class_name]["angles_max"][idx]:
            raise exception_class(
                "Has invalid angle value, error on index {0}. Received {3} but angle should be {1} ~ {2}.".format(
                    idx, robot_limit[class_name]["angles_min"][idx], robot_limit[class_name]["angles_max"][idx], angle
                )
            )


def check_0_or_1(parameter, value, range_data, value_type, exception_class, _type):
    check_value_type(parameter, value_type, exception_class, _type)
    if value not in range_data:
        error = "The data supported by parameter {} is ".format(parameter)
        len_data = len(range_data)
        for idx in range(len_data):
            error += str(range_data[idx])
            if idx != len_data - 1:
                error += " or "
        error += ", but the received value is {}".format(value)
        raise exception_class(error)


def check_id(value, id_list, exception_class):
    raise exception_class(
        "The joint_id not right, should be in {0}, but received {1}.".format(
            id_list, value
        )
    )


def calibration_parameters(**kwargs):
    # with open(os.path.dirname(os.path.abspath(__file__))+"/robot_limit.json") as f:
    robot_limit = RobotLimit.robot_limit
    parameter_list = list(kwargs.keys())
    # class_name = kwargs.get("class_name", None)
    class_name = "Pro450Client"
    if class_name in ["Pro450Client"]:
        for parameter in parameter_list[1:]:
            value = kwargs.get(parameter, None)
            value_type = type(value)
            if parameter == "pin_no_base":
                check_0_or_1(parameter, value, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], value_type,
                             MyCobotPro450DataException,
                             int)
            elif parameter == "pin_no":
                check_0_or_1(parameter, value, [1, 2], value_type, MyCobotPro450DataException, int)
            elif parameter == ['pin_signal', 'value', 'state']:
                check_0_or_1(parameter, value, [0, 1], value_type, MyCobotPro450DataException, int)

            elif parameter == 'joint_id':
                if value not in robot_limit[class_name][parameter]:
                    check_id(value, robot_limit[class_name][parameter], MyCobotPro450DataException)
            elif parameter == ["servo_restore", "set_motor_enabled"]:
                if value not in [1, 2, 3, 4, 5, 6, 254]:
                    raise MyCobotPro450DataException(
                        "The joint_id should be in [1,2,3,4,5,6,254], but received {}".format(value))
            elif parameter == 'angle':
                joint_id = kwargs.get('joint_id', None)
                index = robot_limit[class_name]['joint_id'][joint_id - 1] - 1
                if value < robot_limit[class_name]["angles_min"][index] or value > \
                        robot_limit[class_name]["angles_max"][
                            index]:
                    raise MyCobotPro450DataException(
                        "angle value not right, should be {0} ~ {1}, but received {2}".format(
                            robot_limit[class_name]["angles_min"][index], robot_limit[class_name]["angles_max"][index],
                            value
                        )
                    )
            elif parameter == 'speed':
                if not 1 <= value <= 100:
                    raise MyCobotPro450DataException(
                        "speed value not right, should be 1 ~ 100, the error speed is %s"
                        % value
                    )
            elif parameter == 'coord':
                coord_id = kwargs.get('coord_id', None)
                index = robot_limit[class_name]['coord_id'][coord_id - 1] - 1  # Get the index based on the ID

                if value < robot_limit[class_name]["coords_min"][index] or value > \
                        robot_limit[class_name]["coords_max"][index]:
                    raise MyCobotPro450DataException(
                        "Coordinate value not right, should be {0} ~ {1}, but received {2}".format(
                            robot_limit[class_name]["coords_min"][index],
                            robot_limit[class_name]["coords_max"][index],
                            value
                        )
                    )
            elif parameter == "angles":
                check_angles(value, robot_limit, class_name, MyCobotPro450DataException)
            elif parameter == 'coords':
                check_coords(parameter, value, robot_limit, class_name, MyCobotPro450DataException)


def get_base_io_input(angles, speed):
    """Get the input IO status of the base

    Args:
        pin_no: (int) pin port number. range 1 ~ 12
    """
    calibration_parameters(class_name="Pro450Client", coords=angles, speed=speed)
    # return self._mesg(ProtocolCode.GET_BASIC_INPUT, pin_no)


if __name__ == '__main__':
    res = get_base_io_input([75, 325, 142, 180, 24, 85], 120)
    print(res)
