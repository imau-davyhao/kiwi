import pyrealsense2 as rs
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


pollination_distance = 250


def convert_points_to_world_coordinates(points, depth_frame, intrinsics):
    points = np.array(points, dtype=int)
    if points.size == 0:
        print("未检测到点，无法进行转换操作")
        return np.empty((0, 3), dtype=np.float32)

    height, width = depth_frame.shape[:2]
    valid_pixel_mask = (
        (points[:, 0] >= 0)
        & (points[:, 0] < width)
        & (points[:, 1] >= 0)
        & (points[:, 1] < height)
    )
    points = points[valid_pixel_mask]
    if points.size == 0:
        print("检测点全部超出深度图范围，无法进行转换操作")
        return np.empty((0, 3), dtype=np.float32)

    depth_values = depth_frame[points[:, 1], points[:, 0]]
    valid_depth_mask = depth_values > 0
    points = points[valid_depth_mask]
    depth_values = depth_values[valid_depth_mask]
    if points.size == 0:
        print("检测点深度值无效，无法进行转换操作")
        return np.empty((0, 3), dtype=np.float32)

    z = depth_values - pollination_distance
    x = (points[:, 0] - intrinsics.ppx) * z / intrinsics.fx
    y = (points[:, 1] - intrinsics.ppy) * z / intrinsics.fy
    world_points = np.vstack((x, y, z)).T
    return world_points
