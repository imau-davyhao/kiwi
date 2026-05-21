import numpy as np
import math


def check_quadrant(world_coordinates, idx, tcp_pose):
    if world_coordinates is None or len(world_coordinates) == 0:
        return np.empty((0, 3), dtype=float)

    coords = np.array(world_coordinates, dtype=float).copy()

    # 相机相对 TCP 工具的偏移量，单位 mm。
    a = 32.5
    b = 31.6
    c = 26.7

    offset_x_factor = tcp_pose[0]
    offset_y_factor = tcp_pose[1]
    offset_z_factor = tcp_pose[2]

    offset_x = offset_x_factor - a
    offset_y = offset_y_factor - b
    offset_z = offset_z_factor - c

    coords[:, 0] += offset_x
    coords[:, 1] += offset_y
    coords[:, 2] += offset_z

    quadrant1 = np.logical_and(coords[:, 0] > 0, np.logical_and(coords[:, 1] > 0, coords[:, 2] > 0))
    quadrant2 = np.logical_and(coords[:, 0] < 0, np.logical_and(coords[:, 1] > 0, coords[:, 2] > 0))
    quadrant3 = np.logical_and(coords[:, 0] < 0, np.logical_and(coords[:, 1] < 0, coords[:, 2] > 0))
    quadrant4 = np.logical_and(coords[:, 0] > 0, np.logical_and(coords[:, 1] < 0, coords[:, 2] > 0))

    not_in_any_quadrant = np.logical_not(
        np.logical_or(np.logical_or(np.logical_or(quadrant1, quadrant2), quadrant3), quadrant4)
    )
    if np.any(not_in_any_quadrant):
        print("存在不在任何象限的坐标")

    quadrant1_coords = coords[quadrant1]
    quadrant2_coords = coords[quadrant2]
    quadrant3_coords = coords[quadrant3]
    quadrant4_coords = coords[quadrant4]

    if idx == 1:
        return quadrant1_coords
    elif idx == 2:
        return quadrant2_coords
    elif idx == 3:
        return quadrant3_coords
    elif idx == 4:
        return quadrant4_coords
    else:
        print("无效的象限索引，请输入 1 到 4 之间的整数。")
        return np.empty((0, 3), dtype=float)


def is_within_workspace(x, y, z):
    sphere_center_z = 87.45
    sphere_radius = 950
    if math.sqrt(x**2 + y**2 + (z - sphere_center_z) ** 2) > sphere_radius:
        return False

    plane_z = 400
    if z < plane_z:
        return False

    cylinder_radius = 100
    if math.sqrt(x**2 + y**2) < cylinder_radius:
        return False

    return True


# world_coordinates = np.array([[-235.74124072,  392.6520078,   786.        ],
#  [ -14.49239423,  402.51875541,  857.        ],
#  [   3.02463912,  355.35751177,  857.        ],
#  [-722.36049252,  275.33312734,  923.        ],
#  [-411.55337329,  365.41973114,  916.        ]])

# quadrants = [
#         [0.4, 0.4, 0, 0, 0, 1.57]
#         # [-0.5, 0.5, 0.1, 0, 0, 0],
#         # [-0.5, -0.5, 0.1, 0, 0, 0],
#         # [0.5, -0.5, 0.1, 0, 0, 0]
#     ]
# quadrant_coords = check_quadrant(world_coordinates, 1, quadrants)
# # print('xxxxxxxxxxxxxxxx',quadrant_coords)


def filter_coordinates_within_workspace(quadrant_coords):
    if quadrant_coords is None or len(quadrant_coords) == 0:
        return np.empty((0, 3), dtype=float)

    filtered_coords = [
        coord for coord in quadrant_coords
        if is_within_workspace(coord[0], coord[1], coord[2])
    ]
    filtered_coords = np.array(filtered_coords, dtype=float)

    if filtered_coords.size == 0:
        return np.empty((0, 3), dtype=float)

    return filtered_coords


# # # 假设 quadrant_coords 是由 check_quadrant 函数返回的坐标列表
# # # 调用上述函数并打印结果
# filtered_quadrant_coords = filter_coordinates_within_workspace(quadrant_coords)
# print('00',filtered_quadrant_coords)
