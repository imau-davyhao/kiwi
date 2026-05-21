# Kiwi Pollination Robot

![Pollination Robot](images/pollination%20robot.png)

本项目用于猕猴桃授粉机器人的室内演示与流程验证。系统结合 RealSense 深度相机、YOLO/ONNX 目标检测、三维坐标转换、空间路径规划和 UR 机械臂控制，实现从花朵识别到机械臂定点授粉的闭环流程。

## 功能概览

- **图像采集**：使用 Intel RealSense 同步采集 RGB 图像和深度图像，并将深度图对齐到 RGB 图。
- **花朵检测**：加载 ONNX 格式的 YOLO 模型，识别 RGB 图像中的猕猴桃花朵位置。
- **坐标转换**：根据深度值和相机内参，将图像坐标转换为三维世界坐标。
- **空间筛选**：按照机械臂工作象限和工作空间约束过滤目标点。
- **路径规划**：使用贪心算法生成局部最优授粉路径，并输出三维路径可视化结果。
- **机械臂执行**：通过 RTDE 控制 UR 机械臂移动到目标点，并触发授粉执行信号。

## 工作流程

1. 采用 Eye-in-Hand 相机布置方式，将相机安装在机械臂末端，以扩大识别范围并减少机械臂本体遮挡。
2. 启动防碰撞与初始化流程，机械臂从当前位置移动到安全过渡点，再进入拍照位置。
3. 使用笛卡尔坐标逆解控制机械臂运动到指定拍照点。
4. 启动 RealSense 相机，等待曝光和白平衡稳定后采集 RGB 与 Depth 图像。
5. 使用 YOLO/ONNX 模型识别花朵，获得 RGB 图像中的目标中心点。
6. 将 RGB 目标点映射到对齐后的深度图，结合深度值计算真实三维坐标。
7. 按象限和工作空间限制筛选目标点，剔除机械臂不可达或不适合执行的点。
8. 使用贪心算法规划授粉顺序，生成并保存三维路径图。
9. 将规划后的坐标发送给 UR 机械臂，依次移动到目标点并触发授粉信号。
10. 当前象限完成后，机械臂移动到过渡点并进入下一个象限，直至遍历全部工作区域。

## 项目结构

| 文件 | 说明 |
| --- | --- |
| `main.py` | 主流程入口，串联机械臂运动、图像采集、目标识别、路径规划和授粉执行 |
| `catch_image.py` | RealSense RGB/Depth 图像采集、对齐与保存 |
| `onnx_flower.py` | ONNX 模型加载与花朵目标检测 |
| `world_coordinates.py` | 图像坐标到世界坐标的转换 |
| `check_quadrant.py` | 象限判断与机械臂工作空间过滤 |
| `greedy_path.py` | 贪心路径规划与三维路径可视化 |
| `move.py` | UR 机械臂 RTDE 控制与授粉信号触发 |
| `REDT_angle_get.py` | 机械臂关节角采集与记录 |
| `jc.py` | 串口设备检测工具 |

## 环境依赖

项目主要依赖以下 Python 库和硬件 SDK：

- `numpy`
- `opencv-python`
- `matplotlib`
- `pandas`
- `pyrealsense2`
- `rtde-control`
- `rtde-receive`
- `rtde-io`

硬件环境：

- Intel RealSense 深度相机
- UR 系列机械臂
- 可通过 RTDE 访问的 UR 控制柜
- 授粉执行机构及对应 I/O 触发电路

## 快速开始

1. 安装依赖：

   ```bash
   pip install numpy opencv-python matplotlib pandas pyrealsense2 rtde-control rtde-receive rtde-io
   ```

2. 确认机械臂 IP 配置：

   ```python
   robot_ip = "192.168.56.10"
   ```

   如现场网络配置不同，请同步修改 `move.py` 和 `REDT_angle_get.py` 中的 IP 地址。

3. 确认模型文件存在：

   ```text
   best.onnx
   ```

   默认检测模型在 `onnx_flower.py` 中配置：

   ```python
   onnx_model_path = "best.onnx"
   ```

4. 运行主程序：

   ```bash
   python main.py
   ```

## 输出文件

程序运行过程中会生成或更新以下文件：

- `color_image.png`：最近一次采集的 RGB 图像
- `depth_image.png`：最近一次采集的深度图像
- `results/`：识别结果图像输出目录
- `raw_date/`：原始采集图像和路径规划图输出目录
- `joint_angles_data.csv`：机械臂关节角记录文件

## 当前限制

- 受机械臂结构影响，机器人上方约 200 mm 直径范围内暂不适合执行授粉作业。
- 当前路径规划以局部贪心策略为主，后续可进一步研究全局最优授粉路径。
- 已尝试 UWB 和视觉导航方案，效果仍需改进，后续计划测试 MID-70 激光雷达导航。
- 猕猴桃园地面起垄会影响履带底盘运动稳定性，后续需要结合底盘结构和作业路径进一步优化。

## 注意事项

- 运行主流程前，请确认机械臂周围无人员和障碍物，并完成现场安全检查。
- RTDE 控制会直接驱动机械臂运动，建议先在仿真或低速模式下验证坐标、姿态和工作空间限制。
- `results/` 和 `raw_date/` 目录需要在运行前存在，否则保存图像时可能报错。
