# -*- coding: utf-8 -*-
"""
=================================================================
区域选择模块 (Region Selection Module)
=================================================================

功能说明:
    这个模块负责让用户用鼠标选择屏幕上的一个矩形区域
    选择完成后，返回区域的坐标和尺寸

核心类:
    RegionSelector - 屏幕区域选择器

工作原理:
    1. 截取当前屏幕的截图
    2. 创建一个全屏窗口显示截图
    3. 监听鼠标事件（点击、拖拽、释放）
    4. 在窗口上绘制选中的矩形框
    5. 用户按 Enter 确认后，返回区域坐标

技术实现:
    - pyautogui: 用于截取屏幕截图
    - OpenCV (cv2): 用于创建窗口、绘制图形、处理图像
    - NumPy: 用于处理图像数据

依赖说明:
    - pyautogui: 屏幕截图和鼠标控制
    - cv2 (OpenCV): 计算机视觉库，用于窗口和图形绘制
    - numpy: NumPy 数值计算库，用于处理图像数组

用户操作说明:
    1. 程序启动后，会弹出一个全屏窗口
    2. 在窗口上点击并拖拽鼠标，选择一个矩形区域
    3. 选中的区域会显示为亮绿色
    4. 未选中的区域会变暗（遮罩效果）
    5. 按 Enter 或 C 键确认选择
    6. 按 Esc 键取消选择
=================================================================
"""

# ======================
# 导入必要的模块
# ======================

# pyautogui: 屏幕截图和鼠标/键盘控制库
# screenshot() 方法可以截取屏幕图片
import pyautogui

# cv2: OpenCV 库
# 用于创建窗口、显示图片、绘制图形、处理图像
# OpenCV 是一个强大的计算机视觉库
import cv2

# numpy: NumPy 数值计算库
# 用于处理图像数据（图像在内存中以 NumPy 数组形式存储）
import numpy as np

# typing: 类型提示模块
# 用于声明函数参数和返回值的类型
from typing import Tuple, Optional


class RegionSelector:
    """
    屏幕区域选择器

    这个类负责让用户通过鼠标拖拽选择屏幕区域

    主要功能:
        1. 截取当前屏幕
        2. 创建全屏选择窗口
        3. 监听鼠标事件
        4. 绘制选择框和遮罩效果
        5. 返回选中的区域坐标

    使用示例:
        # 创建选择器
        selector = RegionSelector()

        # 让用户选择区域
        region = selector.select_region()

        # 检查是否选择成功
        if region:
            x, y, width, height = region
            print(f"选中了区域: ({x}, {y}, {width}, {height})")
        else:
            print("用户取消了选择")

    坐标格式说明:
        返回值是一个四元组: (x, y, width, height)
        - x: 区域左上角的 X 坐标（水平位置）
        - y: 区域左上角的 Y 坐标（垂直位置）
        - width: 区域的宽度（像素）
        - height: 区域的高度（像素）

        例如: (100, 200, 500, 300)
        表示从屏幕 (100, 200) 开始，宽 500 像素，高 300 像素的矩形区域
    """

    def __init__(self):
        """
        初始化区域选择器

        这个方法创建选择器并初始化内部状态

        初始化的内容:
            1. coords: 存储坐标信息的字典
            2. window_name: 窗口标题
        """
        # 坐标字典，存储选择过程中的各种坐标
        self.coords = {
            "ix": -1,      # 起始点的 X 坐标
            "iy": -1,      # 起始点的 Y 坐标
            "x_end": -1,   # 结束点的 X 坐标
            "y_end": -1,   # 结束点的 Y 坐标
            "drawing": False  # 是否正在拖拽中
        }

        # 窗口标题
        self.window_name = "选择播报区域 - 按 Enter/C 确认, Esc 退出"

    def _mouse_callback(self, event: int, x: int, y: int, flags: int, param: dict) -> None:
        """
        鼠标回调函数

        这个函数是给 OpenCV 调用的
        每当鼠标发生特定事件时，OpenCV 会调用这个函数
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            if not param["drawing"]:
                param["drawing"] = True
                param["ix"], param["iy"] = x, y
                param["x_end"], param["y_end"] = x, y

        elif event == cv2.EVENT_MOUSEMOVE:
            if param["drawing"]:
                param["x_end"], param["y_end"] = x, y

        elif event == cv2.EVENT_LBUTTONUP:
            param["drawing"] = False
            param["x_end"], param["y_end"] = x, y

    def select_region(self) -> Optional[Tuple[int, int, int, int]]:
        """
        弹出全屏窗口，让用户拖拽选择区域

        返回值:
            如果用户确认选择，返回 (x, y, width, height)
            如果用户取消选择，返回 None
        """
        # 截取屏幕
        screenshot = pyautogui.screenshot()
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # 创建全屏窗口
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback(self.window_name, self._mouse_callback, param=self.coords)

        while True:
            img_copy = img.copy()

            # 绘制选中的矩形
            if self.coords["drawing"]:
                cv2.rectangle(
                    img_copy,
                    (self.coords["ix"], self.coords["iy"]),
                    (self.coords["x_end"], self.coords["y_end"]),
                    (0, 255, 0),
                    2
                )
            elif self.coords["ix"] != -1 and self.coords["iy"] != -1:
                cv2.rectangle(
                    img_copy,
                    (self.coords["ix"], self.coords["iy"]),
                    (self.coords["x_end"], self.coords["y_end"]),
                    (0, 255, 0),
                    2
                )

            # 绘制遮罩效果
            self._draw_mask(img_copy)

            cv2.imshow(self.window_name, img_copy)
            key = cv2.waitKey(1) & 0xFF

            # Esc 退出
            if key == 27:
                cv2.destroyAllWindows()
                return None

            # Enter 或 C 确认
            if key == 13 or key == ord("c"):
                if (self.coords["ix"] != -1 and self.coords["iy"] != -1 and
                    self.coords["x_end"] != -1 and self.coords["y_end"] != -1):
                    break

        cv2.destroyAllWindows()
        return self._get_roi_coordinates()

    def _draw_mask(self, img: np.ndarray) -> None:
        """
        绘制遮罩效果

        未选中的区域会变暗，突出显示选中的区域
        """
        if self.coords["ix"] == -1:
            return

        # 创建遮罩
        mask = np.zeros(img.shape, dtype=np.uint8)
        roi_corners = np.array([[(
            self.coords["ix"],
            self.coords["iy"]
        ), (
            self.coords["x_end"],
            self.coords["iy"]
        ), (
            self.coords["x_end"],
            self.coords["y_end"]
        ), (
            self.coords["ix"],
            self.coords["y_end"]
        )]], dtype=np.int32)

        channel_count = img.shape[2]
        ignore_mask_color = (255,) * channel_count
        cv2.fillPoly(mask, roi_corners, ignore_mask_color)

        # 反转遮罩并应用变暗效果
        inverse_mask = cv2.bitwise_not(mask)
        opacity = -0.3
        cv2.addWeighted(inverse_mask, opacity, img, 1, 0, img)

    def _get_roi_coordinates(self) -> Tuple[int, int, int, int]:
        """
        获取标准化后的区域坐标
        """
        x_start = min(self.coords["ix"], self.coords["x_end"])
        y_start = min(self.coords["iy"], self.coords["y_end"])
        width = abs(self.coords["x_end"] - self.coords["ix"])
        height = abs(self.coords["y_end"] - self.coords["iy"])

        return (x_start, y_start, width, height)
