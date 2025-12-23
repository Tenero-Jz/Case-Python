# robot_controller.py
import numpy as np
import time

try:
    from Pro450.pymycobot import Pro450Client  # hypothetical import; replace with your actual package name

    HAVE_ROBOT = True
except Exception:
    HAVE_ROBOT = False


class RobotController:
    """
    Wrapper to control MyCobot Pro450. If pymycobot is not available, runs in SIM mode.
    Must set:
      - hand_eye (4x4 numpy) : transform from end-effector to camera (ee -> cam)
      - base_T_ee (4x4) read from robot at runtime for transforms
      - intrinsics (dict) for vision deprojection
    """

    def __init__(self, com_port=None, baudrate=115200, sim=False):
        self.sim = sim or (not HAVE_ROBOT)
        self.com_port = com_port
        self.baudrate = baudrate
        self.robot = None
        if not self.sim:
            try:
                # Replace MyCobotPro with your actual class and init signature
                self.robot = Pro450Client(self.com_port, self.baudrate)
            except Exception as e:
                print("Failed to init real robot, falling back to simulation:", e)
                self.sim = True
        # default hand-eye (identity, must be overwritten by real calibration)
        self.T_ee_cam = np.eye(4, dtype=np.float64)
        # current base->ee pose cache (4x4)
        self.T_base_ee = np.eye(4, dtype=np.float64)
        # mapping gains for pixel->angle (deg per pixel) for send_angles_delta
        self.pix_to_deg_gain = np.array([0.05, 0.03])  # tune these!
        # joint limits safety (min,max) deg for 6 joints; user should adjust
        self.joint_limits = [(-180, 180)] * 6

    def wait(self, t):
        time.sleep(t)

    def move_to_initial(self, angles_deg, wait=True):
        """Move to initial pose (angles list of 6 deg)."""
        if self.sim:
            print("SIM: move_to_initial", angles_deg)
        else:
            # replace with actual API
            self.robot.send_angles(angles_deg, 50)
        if wait:
            time.sleep(1.0)

    def get_current_angles(self):
        if self.sim:
            return [0, 0, 0, 0, 0, 0]
        else:
            # replace with actual API to read angles
            return self.robot.get_angles()

    def update_base_T_ee(self, T):
        """Set cached base->ee transform"""
        self.T_base_ee = T.copy()

    def send_angles_delta_from_pixels(self, dx_pix, dy_pix):
        """
        Map pixel deltas to small joint angle deltas and call send_angles.
        This is a simple heuristic controller for follow behavior.
        """
        da1 = float(-dx_pix * self.pix_to_deg_gain[0])  # joint 1 (yaw)
        da2 = float(dx_pix * 0.0 + dy_pix * self.pix_to_deg_gain[1])  # joint 2 (pitch)
        cur = self.get_current_angles()
        new = cur.copy()
        # apply to joint 1 and 2 (indexes 0 and 1)
        new[0] = cur[0] + da1
        new[1] = cur[1] + da2
        # clamp
        for i in range(6):
            mn, mx = self.joint_limits[i]
            new[i] = max(mn, min(mx, new[i]))
        if self.sim:
            print(f"SIM: send_angles -> {new} (delta {da1:.3f},{da2:.3f})")
        else:
            self.robot.send_angles(new, 50)

    def move_linear_to(self, xyz_rpy, speed=50):
        """
        Move end-effector in Cartesian coords using send_coords() API.
        xyz_rpy: [x(mm), y(mm), z(mm), rx, ry, rz] in robot base frame units expected by API.
        """
        if self.sim:
            print("SIM: move_linear_to", xyz_rpy)
        else:
            self.robot.send_coords(xyz_rpy, speed, 0)  # signature may vary

    def gripper_open(self):
        if self.sim:
            print("SIM: gripper_open")
        else:
            try:
                self.robot.set_gripper_state(open=True)
            except Exception:
                pass

    def gripper_close(self):
        if self.sim:
            print("SIM: gripper_close")
        else:
            try:
                self.robot.set_gripper_state(open=False)
            except Exception:
                pass

    def cam_point_to_base(self, cam_point_xyz):
        """
        Convert camera coordinates (x,y,z) in meters to base coordinates in meters using:
        base_T_cam = base_T_ee * ee_T_cam
        cam_point_xyz: (3,) in meters
        returns base_point (3,) in meters
        """
        p_cam = np.array([cam_point_xyz[0], cam_point_xyz[1], cam_point_xyz[2], 1.0], dtype=np.float64)
        base_T_cam = self.T_base_ee @ np.linalg.inv(self.T_ee_cam)
        p_base = base_T_cam @ p_cam
        return p_base[:3]
