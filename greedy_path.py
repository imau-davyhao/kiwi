import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime
from pathlib import Path
# 贪心算法规划路径
def greedy_path_planning(points):
    if len(points) == 0:
        return []

    # 初始化路径，包含起始点
    path = [points[0].tolist()]  # 使用 tolist() 转换为列表
    # 剩余点集合，移除起始点
    remaining_points = points[1:]
    
    while len(remaining_points) > 0:
        # 计算当前点到所有剩余点的距离
        distances = np.linalg.norm(remaining_points - path[-1], axis=1)
        # 找到最近的点的索引
        nearest_index = np.argmin(distances)
        # 将最近的点添加到路径中
        path.append(remaining_points[nearest_index].tolist())
        # 从剩余点集合中移除已经选择的点
        remaining_points = np.delete(remaining_points, nearest_index, axis=0)
    
    return path

def visualize_path(path):
    if len(path) == 0:
        return

    # 创建一个新的图和三维子图
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # 提取路径中的 x, y, z 坐标
    x_coords, y_coords, z_coords = zip(*path)

    # 绘制路径点
    ax.scatter(x_coords, y_coords, z_coords, c='r', marker='o')

    # 绘制连接路径的线
    ax.plot(x_coords, y_coords, z_coords, c='b')

    # 标记每个点的索引（顺序）
    for i, (x, y, z) in enumerate(zip(x_coords, y_coords, z_coords)):
        ax.text(x, y, z, f' {i}', color='black', fontsize=9)

    # 设置坐标轴标签
    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')
    ax.set_zlabel('Z coordinate')

    # 设置坐标轴范围与点的范围一致，以便更好地展示
    ax.set_xlim(min(x_coords), max(x_coords))
    ax.set_ylim(min(y_coords), max(y_coords))
    ax.set_zlim(min(z_coords), max(z_coords))

    # 获取当前时间字符串
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # 保存路径
    Path("raw_date").mkdir(exist_ok=True)
    save_path = f"raw_date/PA_{now}.png"

   # 显示图形 1 秒后自动关闭
    plt.show(block=False)
    plt.savefig(save_path, dpi=600)
    plt.pause(1)
    plt.close()

    # 显示图形
    # plt.show()
    # plt.savefig('3d_greedy_path_planning.png', dpi=600)
    # while True:
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #     cv2.destroyAllWindows()

# 调用可视化函数
# visualize_path(planned_path)
