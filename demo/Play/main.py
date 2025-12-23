# main.py
"""
Main demo: Eye-in-Hand color follow and pick demo for MyCobot Pro450 + Gemini2 on Windows.
This is a scaffold: it will try to use real hardware (Orbbec + pymycobot) if available,
otherwise will run in SIMULATION MODE to allow you to test logic and parameters.

How to use:
  1. Edit the CONFIG section below (COM port, intrinsics, hand-eye matrix)
  2. Install requirements: opencv-python, numpy, (your orbbec SDK), (pymycobot)
  3. Run: python main.py
"""

import time, sys, os
import numpy as np
import cv2
from vision import find_color_target, deproject_pixel_to_point
from robot_controller import RobotController

# ---------------- CONFIG ----------------
COM_PORT = "COM3"  # set your robot COM
BAUDRATE = 115200
SIM_MODE = False  # set True to force simulation (no hardware)
INITIAL_ANGLES = [0, -30, 40, 0, 30, 0]  # degrees, example initial pose for inspection
COLOR_LIST = ["red", "green", "blue"]
# Camera intrinsics (fill with your Gemini2 fx,fy,cx,cy)
INTRINSICS = {"fx": 600.0, "fy": 600.0, "cx": 320.0, "cy": 240.0}

# Hand-eye: ee -> cam transformation (4x4). Fill with calibration results.
# For testing you can keep identity and adjust offsets in code.
HAND_EYE_4x4 = np.eye(4, dtype=np.float64)

# Place positions for each color in robot base frame (meters)
PLACE_POS = {
    "red": np.array([0.25, -0.10, 0.05], dtype=np.float64),
    "green": np.array([0.25, 0.00, 0.05], dtype=np.float64),
    "blue": np.array([0.25, 0.10, 0.05], dtype=np.float64),
}

# thresholds
STOP_PIX_THRESH = 5.0  # pixels
STOP_FRAMES = 10  # frames of low-motion to consider stopped
MIN_AREA = 400  # min contour area for detection
DEPTH_UNITS = 1.0  # depth already in meters from your camera


# ----------------------------------------

def open_camera_simulator():
    """Simple webcam simulator when real depth camera not present. Depth simulated as constant."""
    cap = cv2.VideoCapture(0)
    return cap


def read_frame_sim(cap):
    ret, frame = cap.read()
    if not ret:
        return None, None
    h, w = frame.shape[:2]
    depth = np.full((h, w), 0.30, dtype=np.float32)  # 30 cm constant depth for simulation
    return frame, depth


def main_loop():
    # init robot controller
    rc = RobotController(COM_PORT, BAUDRATE, sim=SIM_MODE)
    rc.T_ee_cam = HAND_EYE_4x4.copy()
    rc.update_base_T_ee(np.eye(4))  # user must update with real reading if available

    # move to initial
    rc.move_to_initial(INITIAL_ANGLES, wait=True)

    # try to open real Gemini2 camera: user should replace with their SDK code.
    use_sim_cam = True
    cap = None
    try:
        # Attempt to detect default camera via OpenCV (will use webcam if no SDK)
        cap = open_camera_simulator()
        use_sim_cam = True
    except Exception as e:
        print("Camera init failed, falling back to simulation:", e)
        use_sim_cam = True
        cap = open_camera_simulator()

    # main state
    state = "FOLLOW"
    last_positions = []
    target_color_current = None
    frames_since_detect = 0
    prev_time = time.time()

    print("Starting main loop. Press 'q' in the display window to quit.")

    while True:
        if use_sim_cam:
            frame, depth = read_frame_sim(cap)
        else:
            frame, depth = read_frame_sim(cap)  # placeholder for real SDK read

        if frame is None:
            print("Frame None, exiting")
            break

        display = frame.copy()
        found_any = False
        for color in COLOR_LIST:
            u, v, depth_m, area, mask = find_color_target(color, frame, depth, min_area=MIN_AREA)
            if u is None:
                continue
            found_any = True
            target_color_current = color
            # draw
            cv2.circle(display, (u, v), 6, (0, 255, 0), -1)
            cv2.putText(display, f"{color} {area:.0f}", (u + 10, v), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            # follow logic: compute pixel delta to image center
            H, W = frame.shape[:2]
            u0, v0 = W // 2, H // 2
            dx = (u - u0)
            dy = (v - v0)
            # Send small angle adjustments using send_angles() mapping
            rc.send_angles_delta_from_pixels(dx, dy)
            # store motion history for stop detection
            last_positions.append((u, v, depth_m, time.time()))
            if len(last_positions) > STOP_FRAMES:
                last_positions.pop(0)
            # stop detection: compute average pixel motion
            if len(last_positions) >= 2:
                motions = [np.hypot(last_positions[i][0] - last_positions[i - 1][0],
                                    last_positions[i][1] - last_positions[i - 1][1]) for i in
                           range(1, len(last_positions))]
                avg_motion = sum(motions) / len(motions)
            else:
                avg_motion = 1000
            # if stopped, go to grab sequence
            if avg_motion < STOP_PIX_THRESH:
                print("Detected stop for color", color)
                # compute median last depth/uv
                u_med = int(np.median([p[0] for p in last_positions]))
                v_med = int(np.median([p[1] for p in last_positions]))
                depth_med = np.median([p[2] for p in last_positions if p[2] is not None])
                if depth_med is None:
                    print("Depth unknown, abort grab")
                else:
                    # deproject to camera coords (meters)
                    cam_pt = deproject_pixel_to_point(u_med, v_med, depth_med, INTRINSICS)
                    # convert to base coords
                    base_pt = rc.cam_point_to_base(cam_pt)
                    print("Object base coords (m):", base_pt)
                    # perform pick: converting to robot mm and rpy placeholder
                    pre = np.array(
                        [base_pt[0] * 1000, base_pt[1] * 1000, (base_pt[2] * 1000) + 70, 180, 0, 0])  # mm, rx,ry,rz
                    grasp = np.array([base_pt[0] * 1000, base_pt[1] * 1000, (base_pt[2] * 1000) + 10, 180, 0, 0])
                    rc.move_linear_to(pre, speed=50)
                    rc.move_linear_to(grasp, speed=30)
                    rc.gripper_close()
                    time.sleep(0.4)
                    rc.move_linear_to(pre, speed=50)
                    # move to place pos
                    place_m = PLACE_POS.get(color, PLACE_POS["red"])
                    place_mm = np.array([place_m[0] * 1000, place_m[1] * 1000, place_m[2] * 1000 + 70, 180, 0, 0])
                    rc.move_linear_to(place_mm, speed=60)
                    place_down = place_mm.copy();
                    place_down[2] = place_m[2] * 1000 + 10
                    rc.move_linear_to(place_down, speed=30)
                    rc.gripper_open()
                    time.sleep(0.3)
                    rc.move_linear_to(place_mm, speed=60)
                    # return to initial inspection pose
                    rc.move_to_initial(INITIAL_ANGLES, wait=True)
                    last_positions.clear()

        # UI
        cv2.imshow("Eye-in-Hand Follow", display)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main_loop()
