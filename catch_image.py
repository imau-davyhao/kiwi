import pyrealsense2 as rs
import numpy as np
import cv2
import time
import datetime
from pathlib import Path


def capture_and_save():
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    Path("raw_date").mkdir(exist_ok=True)

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

    pipeline.start(config)
    try:
        color_sensor = pipeline.get_active_profile().get_device().query_sensors()[1]
        color_sensor.set_option(rs.option.enable_auto_exposure, 0)
        color_sensor.set_option(rs.option.exposure, 50)

        depth_sensor = pipeline.get_active_profile().get_device().first_depth_sensor()
        depth_sensor.set_option(rs.option.enable_auto_exposure, 0)
        depth_sensor.set_option(rs.option.exposure, 4)
        depth_sensor.set_option(rs.option.laser_power, 300)

        profile = pipeline.get_active_profile()
        color_intrinsics = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()

        align = rs.align(rs.stream.color)
        time.sleep(2)

        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        if not depth_frame or not color_frame:
            raise RuntimeError("RealSense did not return both depth and color frames.")

        depth_image = np.asarray(depth_frame.get_data(), dtype=np.float32)
        color_image = np.asanyarray(color_frame.get_data())
        depth_image_uint16 = depth_image.astype(np.uint16)

        cv2.imwrite("color_image.png", color_image)
        cv2.imwrite(f"raw_date/CL_{now}.png", color_image)
        cv2.imwrite("depth_image.png", depth_image_uint16)
        cv2.imwrite(f"raw_date/depth_{now}.png", depth_image_uint16)

        return color_image, depth_image, color_intrinsics
    finally:
        pipeline.stop()


# ***********************函数测试代码*********************

# def main():
#     capture_and_save()

# if __name__ == "__main__":
#     main()

# ********************可视化测试代码*********************
def main():
    Path("results").mkdir(exist_ok=True)
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

    try:
        pipeline.start(config)

        color_sensor = pipeline.get_active_profile().get_device().query_sensors()[1]
        color_sensor.set_option(rs.option.enable_auto_exposure, 0)
        color_sensor.set_option(rs.option.exposure, 100)

        depth_sensor = pipeline.get_active_profile().get_device().first_depth_sensor()
        depth_sensor.set_option(rs.option.enable_auto_exposure, 0)
        depth_sensor.set_option(rs.option.exposure, 5000)
        depth_sensor.set_option(rs.option.laser_power, 300)

        align = rs.align(rs.stream.color)

        while True:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)

            depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()

            if depth_frame and color_frame:
                depth_image = np.asarray(depth_frame.get_data(), dtype=np.float32)
                color_image = np.asanyarray(color_frame.get_data())

                depth_colormap = cv2.applyColorMap(
                    cv2.convertScaleAbs(depth_image, alpha=0.03),
                    cv2.COLORMAP_VIRIDIS,
                )

                cv2.namedWindow("Color Image", cv2.WINDOW_AUTOSIZE)
                cv2.namedWindow("Aligned Depth Image", cv2.WINDOW_AUTOSIZE)

                cv2.imshow("Color Image", color_image)
                cv2.imshow("Aligned Depth Image", depth_colormap)

                key = cv2.waitKey(1)
                if key & 0xFF == ord("s"):
                    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    cv2.imwrite("color_image.png", color_image)
                    cv2.imwrite(f"results/CL_{now}.png", color_image)
                    depth_image_uint16 = depth_image.astype(np.uint16)
                    cv2.imwrite("depth_image.png", depth_image_uint16)
                    cv2.imwrite(f"results/DP_{now}.png", depth_image_uint16)
                    print("Images saved.")
                    cv2.destroyAllWindows()
                    break

                elif key & 0xFF == ord("q") or key == 27:
                    cv2.destroyAllWindows()
                    break

    except Exception as e:
        print(f"An error occurred: {e}")
        cv2.destroyAllWindows()
    finally:
        pipeline.stop()


if __name__ == "__main__":
    main()
