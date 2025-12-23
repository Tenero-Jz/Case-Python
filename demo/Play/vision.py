# vision.py
import cv2
import numpy as np

# Simple vision utilities for color detection (HSV-based) and depth handling.
# Exposes: find_color_target(color_name, color_img, depth_img, intrinsics)
# color_name: 'red'|'green'|'blue' (you can extend)
# color_img: BGR numpy array (H,W,3)
# depth_img: depth in meters, same W,H (float32 or float64). If None, depth will be None.
# intrinsics: dict with fx,fy,cx,cy


HSV_PRESETS = {
    "red": [((0, 90, 60), (10, 255, 255)), ((170, 90, 60), (180, 255, 255))],
    "green": [((40, 60, 60), (85, 255, 255))],
    "blue": [((95, 60, 60), (130, 255, 255))],
}


def find_color_target(color_name, color_img, depth_img=None, intrinsics=None, min_area=400):
    """
    Returns (u,v,depth_m,area,mask) or (None,)*5 if not found.
    """
    if color_name not in HSV_PRESETS:
        raise ValueError("Unknown color: " + str(color_name))
    hsv = cv2.cvtColor(color_img, cv2.COLOR_BGR2HSV)
    mask = None
    for (low, high) in HSV_PRESETS[color_name]:
        low = np.array(low, dtype=np.uint8)
        high = np.array(high, dtype=np.uint8)
        m = cv2.inRange(hsv, low, high)
        mask = m if mask is None else cv2.bitwise_or(mask, m)
    # morphology to clean noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, None, None, 0, mask
    c = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(c)
    if area < min_area:
        return None, None, None, area, mask
    M = cv2.moments(c)
    if M['m00'] == 0:
        return None, None, None, area, mask
    u = int(M['m10'] / M['m00'])
    v = int(M['m01'] / M['m00'])
    depth = None
    if depth_img is not None:
        h, w = depth_img.shape[:2]
        # sample small patch to reduce noise
        x0 = max(0, u - 2)
        x1 = min(w - 1, u + 2)
        y0 = max(0, v - 2)
        y1 = min(h - 1, v + 2)
        patch = depth_img[y0:y1 + 1, x0:x1 + 1].astype(np.float32)
        patch = patch[np.isfinite(patch)]
        if patch.size > 0:
            depth = float(np.median(patch))
    return u, v, depth, area, mask


def deproject_pixel_to_point(u, v, depth_m, intrinsics):
    """Convert pixel+depth to camera coordinates (x,y,z) in meters. intrinsics: dict fx,fy,cx,cy"""
    if depth_m is None:
        return None
    fx = intrinsics["fx"]
    fy = intrinsics["fy"]
    cx = intrinsics["cx"]
    cy = intrinsics["cy"]
    x = (u - cx) * depth_m / fx
    y = (v - cy) * depth_m / fy
    z = depth_m
    return np.array([x, y, z], dtype=np.float32)
