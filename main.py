
import numpy as np
import time
from pathlib import Path
from move import move_robot_to_position_cartesian, move_robot_to_position_angel,detecting_location,pollination_signal
from catch_image import capture_and_save
from onnx_flower import recognize
from world_coordinates import convert_points_to_world_coordinates
from check_quadrant import check_quadrant,filter_coordinates_within_workspace
from greedy_path import greedy_path_planning, visualize_path

#定义机器人的一些全局变量
Xaxis_offset=500
Yaxis_offset=400
Zaxis_offset=100

Roll_offset=0
Pitch_offset=0
Yaw_offset=0

def main():
    Path("results").mkdir(exist_ok=True)
    Path("raw_date").mkdir(exist_ok=True)

     # 定义四个象限的拍照位置和过渡位置
    quadrants = [
        [Xaxis_offset, Yaxis_offset, Zaxis_offset, Roll_offset, Pitch_offset, Yaw_offset], # 第1象限
        [-Xaxis_offset, Yaxis_offset, Zaxis_offset, Roll_offset, Pitch_offset, Yaw_offset],  # 第2象限
        [-Xaxis_offset, -Yaxis_offset, Zaxis_offset, Roll_offset, Pitch_offset, Yaw_offset],  # 第3象限
        [Xaxis_offset, -Yaxis_offset, Zaxis_offset, Roll_offset, Pitch_offset, Yaw_offset]  # 第4象限
    ]
    quadrants_temp = [
        [59.9,-121.3,-82.3,-64.9,-90.1,-153.3], # 第1象限过渡角度
        [137.4,-125.1,-81.4,-59.0,-85.5,-230.6], # 第2象限过渡角度
        [-152.5,-124.9,-103.2,-37.1,-85.5,63.2], # 第3象限过渡角度
        [-31.5,-125.7,-95.2,-49.7,-91.0,-62.9] # 第4象限过渡角度
        
    ]
    #自检防碰撞，抬高机械臂
    move_robot_to_position_angel(quadrants_temp[detecting_location()])
    #定义机械臂初始位置
    Start_angel=(88,-126,-104,-38,-90,-180)
    #机械臂来到初始位置
    move_robot_to_position_angel(Start_angel)

                                #↑↑↑↑↑↑机械臂初始化程序↑↑↑↑
#***********************************************************************************************************************************
    for idx, tcp_pose in enumerate(quadrants, start=1):    
        move_robot_to_position_angel(quadrants_temp[idx-1])
        print(f"移动到第{idx}象限过渡位置{quadrants_temp[idx-1]}") 

        move_robot_to_position_cartesian(tcp_pose)
        print(f"移动到第{idx}象限: {tcp_pose}")
        
        time.sleep(1)  # 等待机械臂移动完成，具体时间可根据实际情况调整  


        # # # 第一步：启动相机拍摄GRB和Depth照片，Depth图像对齐到GRB图像，保存在对应的文件夹 **************************   

        color_img_path, depth_image, depth_intrinsics = capture_and_save()
        print(f"第{idx}象限拍照完成")

        # # # 第二步：读取onnx文件，识别GRB照片花朵位置**********************************************************

        points = recognize(color_img_path, 0.3)
        print("图像坐标：", points)
        if not points:  # 如果points为空
            move_robot_to_position_angel(quadrants_temp[idx-1])
            #抬高机械臂防止碰撞
            continue  # 跳过当前循环，继续下一次循环

        # # # 第三步：花朵位置转换为世界坐标********************************************************************

        world_coordinates = convert_points_to_world_coordinates(points, depth_image, depth_intrinsics)
        print("世界坐标：", world_coordinates)

        # # # 第四步：筛选对应象限坐标，并过滤异值点************************************************
        quadrant_coords = check_quadrant(world_coordinates, idx, tcp_pose)
        filtered_quadrant_coords = filter_coordinates_within_workspace(quadrant_coords)
        print("过滤机械臂坐标：", filtered_quadrant_coords)

        # # # 第五步：路径规划*********************************************************************************

        # planned_path = greedy_path_planning(filtered_quadrant_coords)
        # print("规划的路径:", planned_path)
        # # 调用可视化函数
        # visualize_path(planned_path)
        
        if len(filtered_quadrant_coords) == 0:
         print("无可用目标点，跳过路径规划")
         planned_path = np.empty((0, 3))  # 空的二维数组，形状为(0,3)
        else:
         planned_path = greedy_path_planning(filtered_quadrant_coords)
         print("规划的路径:", planned_path)
         # 可视化路径
         visualize_path(planned_path)

        planned_path = np.asarray(planned_path, dtype=float).reshape(-1, 3)

        # # # 第六步：机械臂移动**********************************************************************************
        # 提取 tcp_pose 数组的后三个值
        additional_columns = tcp_pose[-3:]  # 取后三个值

        # 首先，将 additional_columns 转换为 NumPy 数组
        additional_columns_array = np.array(additional_columns)

        # 确保 additional_columns_repeated 的行数与 planned_path 的行数相同
        additional_columns_repeated = np.repeat(additional_columns_array, len(planned_path), axis=0)

        # 现在，将 additional_columns_repeated 转换为二维数组
        # 这里我们使用 reshape(-1, 3)，其中 -1 表示自动计算行数，3 表示每行3个元素
        additional_columns_repeated = additional_columns_repeated.reshape(-1, 3)

        # 现在使用 np.hstack 来水平堆叠，确保两个数组的行数相同
        extended_coords = np.hstack((planned_path, additional_columns_repeated))

        # 遍历 extended_coords 中的每一行
        for row in extended_coords:
            # 将行中的值赋给对应的变量
            x, y, z, roll, pitch, yaw = row
            move_robot_to_position_cartesian(row)
            pollination_signal()

        #第七步：机械臂最终状态**********************************************************************************     

        print(quadrants_temp[idx-1])
        move_robot_to_position_angel(quadrants_temp[idx-1])
    move_robot_to_position_angel(Start_angel)



if __name__ == "__main__":
    main()
    
