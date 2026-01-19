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
            # X 坐标
 起始点的            # 初始值 -1 表示还没有开始选择
            "ix": -1,

            # 起始点的 Y 坐标
            # 初始值 -1 表示还没有开始选择
            "iy": -1,

            # 结束点的 X 坐标
            # 也就是鼠标拖拽结束时的位置
            "x_end": -1,

            # 结束点的 Y 坐标
            "y_end": -1,

            # 是否正在拖拽中
            # True = 鼠标按下，正在拖拽
            # False = 鼠标没有按下
            "drawing": False
        }

        # 窗口标题
        # 显示在选择窗口顶部的文字
        self.window_name = "选择播报区域 - 按 Enter/C 确认, Esc 退出"

    def _mouse_callback(self, event: int, x: int, y: int, flags: int, param: dict) -> None:
        """
        鼠标回调函数

        这个函数是给 OpenCV 调用的
        每当鼠标发生特定事件时，OpenCV 会调用这个函数

        参数说明:
            event: 事件类型
                   - cv2.EVENT_LBUTTONDOWN: 鼠标左键按下
                   - cv2.EVENT_MOUSEMOVE: 鼠标移动
                   - cv2.EVENT_LBUTTONUP: 鼠标左键抬起
            x: 鼠标当前的 X 坐标
            y: 鼠标当前的 Y 坐标
            flags: 额外的标志（如是否有按键同时按下）
            param: 传递给回调函数的参数（我们传入 coords 字典）

        工作流程:
            1. 鼠标按下: 记录起始位置，开始拖拽
            2. 鼠标移动（拖拽中）: 更新结束位置
            3. 鼠标抬起: 结束拖拽，记录最终位置
        """
        # 检查事件类型
        if event == cv2.EVENT_LBUTTONDOWN:
            # 鼠标左键按下

            # 检查是否已经开始拖拽
            if not param["drawing"]:
                # 刚开始拖拽
                # 记录起始位置
                param["drawing"] = True  # 标记为拖拽中
                param["ix"], param["iy"] = x, y  # 记录起始坐标
                param["x_end"], param["y_end"] = x, y  # 结束位置等于起始位置

        elif event == cv2.EVENT_MOUSEMOVE:
            # 鼠标移动

            # 检查是否正在拖拽
            if param["drawing"]:
                # 正在拖拽，更新结束位置
                param["x_end"], param["y_end"] = x, y

        elif event == cv2.EVENT_LBUTTONUP:
            # 鼠标左键抬起

            # 结束拖拽
            param["drawing"] = False
            param["x_end"], param["y_end"] = x, y

    def select_region(self) -> Optional[Tuple[int, int, int, int]]:
        """
        弹出全屏窗口，让用户拖拽选择区域

        这是选择器的主要方法

        工作流程:
            1. 截取当前屏幕
            2. 创建全屏窗口
            3. 设置鼠标回调函数
            4. 进入主循环：
               - 绘制选择框
               - 绘制遮罩效果
               - 显示图片
               - 检查按键（Enter 确认 / Esc 取消）
            5. 返回选中的区域坐标

        返回值:
            如果用户确认选择，返回 (x, y, width, height)
            如果用户取消选择，返回 None

        用户操作:
            - 按住鼠标左键拖拽：选择区域
            - 按 Enter 或 C：确认选择
            - 按 Esc：取消选择
        """
        # ----------------------
        # 第一步：截取屏幕
        # ----------------------

        # 使用 pyautogui 截取整个屏幕
        # 返回一个 PIL Image 对象
        screenshot = pyautogui.screenshot()

        # 将 PIL Image 转换为 NumPy 数组
        # NumPy 是 OpenCV 处理图像的数据格式
        img = np.array(screenshot)

        # 转换颜色通道顺序
        # PIL 使用 RGB 格式，OpenCV 使用 BGR 格式
        # 需要转换，否则颜色会不正确
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # ----------------------
        # 第二步：创建窗口
        # ----------------------

        # 创建窗口
        # cv2.namedWindow() 创建窗口
        # cv2.WINDOW_NORMAL 表示窗口大小可调整
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

        # 设置窗口为全屏
        # cv2.WND_PROP_FULLSCREEN 设置窗口属性
        # cv2.WINDOW_FULLSCREEN 设置为全屏模式
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # 设置鼠标回调函数
        # 当鼠标事件发生时，调用 self._mouse_callback 方法
        # 最后一个参数是传递给回调函数的额外数据（coords 字典）
        cv2.setMouseCallback(self.window_name, self._mouse_callback, param=self.coords)

        # ----------------------
        # 第三步：主循环
        # ----------------------

        # 进入无限循环，持续更新窗口显示
        while True:
            # 创建图片副本
            # 每次循环都从原始图片创建副本
            # 这样可以避免在原图上留下痕迹
            img_copy = img.copy()

            # ----------------------
            # 绘制选择框
            # ----------------------

            # 检查是否正在拖拽
            if self.coords["drawing"]:
                # 正在拖拽，绘制实时选择框
                # cv2.rectangle() 绘制矩形
                # 参数:
                #   img_copy: 在哪个图片上绘制
                #   (ix, iy): 矩形左上角坐标
                #   (x_end, y_end): 矩形右下角坐标
                #   (0, 255, 0): 绿色 (BGR 格式)
                #   2: 线条粗细
                cv2.rectangle(
                    img_copy,
                    (self.coords["ix"], self.coords["iy"]),
                    (self.coords["x_end"], self.coords["y_end"]),
                    (0, 255, 0),
                    2
                )
            elif self.coords["ix"] != -1 and self.coords["iy"] != -1:
                # 拖拽结束，但还没有确认
                # 仍然显示选择框
                cv2.rectangle(
                    img_copy,
                    (self.coords["ix"], self.coords["iy"]),
                    (self.coords["x_end"], self.coords["y_end"]),
                    (0, 255, 0),
                    2
                )

            # ----------------------
            # 绘制遮罩效果
            # ----------------------

            # 未选中的区域会变暗，突出显示选中的区域
            self._draw_mask(img_copy)

            # ----------------------
            # 显示图片
            # ----------------------

            # 在窗口中显示图片
            cv2.imshow(self.window_name, img_copy)

            # 等待按键
            # cv2.waitKey() 等待按键事件
            # 参数 1 表示最多等待 1 毫秒
            # 返回值是按键的 ASCII 码
            key = cv2.waitKey(1) & 0xFF

            # ----------------------
            # 检查按键
            # ----------------------

            # 按 Esc 键 (ASCII 27) 取消选择
            if key == 27:
                # 销毁所有窗口
                cv2.destroyAllWindows()
                # 返回 None 表示取消
                return None

            # 按 Enter 键 (ASCII 13) 或 C 键确认
            if key == 13 or key == ord("c"):
                # 检查是否已经选择了区域
                # 需要所有坐标都有效（不等于 -1）
                if (self.coords["ix"] != -1 and self.coords["iy"] != -1 and
                    self.coords["x_end"] != -1 and self.coords["y_end"] != -1):
                    # 坐标有效，可以退出循环
                    break

        # ----------------------
        # 第四步：清理并返回结果
        # ----------------------

        # 销毁所有窗口
        cv2.destroyAllWindows()

        # 计算并返回标准化的区域坐标
        return self._get_roi_coordinates()

    def _draw_mask(self, img: np.ndarray) -> None:
        """
        绘制遮罩效果

        这个方法让未选中的区域变暗，从而突出显示选中的区域

        工作原理:
            1. 创建一个全黑的遮罩图片
            2. 在遮罩上选中区域的位置填充白色
            3. 反转遮罩（选中区域变黑，未选中区域变白）
            4. 将变暗效果应用到原图

        遮罩效果:
            选中区域: 保持原亮度
            未选中区域: 变暗 30%
        """
        # 检查是否已经开始选择
        if self.coords["ix"] == -1:
            # 还没有开始选择，不需要绘制遮罩
            return

        # 创建全黑遮罩
        # np.zeros() 创建一个全零数组（黑色）
        mask = np.zeros(img.shape, dtype=np.uint8)

        # 定义选中区域的四个角点
        # 格式：[[[x1, y1], [x2, y1], [x2, y2], [x1, y2]]]
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

        # 获取图片的通道数
        # img.shape 返回 (height, width, channels)
        # 例如: (1080, 1920, 3) 表示 1080 高、1920 宽、3 通道
        channel_count = img.shape[2]

        # 创建忽略遮罩颜色（全白色）
        # (255,) * 3 = (255, 255, 255)
        ignore_mask_color = (255,) * channel_count

        # 在遮罩上填充选中区域
        # cv2.fillPoly() 在遮罩上绘制填充的多边形
        cv2.fillPoly(mask, roi_corners, ignore_mask_color)

        # ----------------------
        # 反转遮罩
        # ----------------------

        # 反转遮罩
        # 选中区域变成黑色，未选中区域变成白色
        inverse_mask = cv2.bitwise_not(mask)

        # ----------------------
        # 应用遮罩效果
        # ----------------------

        # 设置遮罩透明度
        # 负值表示变暗
        opacity = -0.3

        # cv2.addWeighted() 混合两张图片
        # 参数:
        #   inverse_mask: 第一张图片（未选中区域）
        #   opacity: 第一张图片的权重
        #   img: 第二张图片（原图）
        #   1: 第二张图片的权重
        #   0: 亮度偏移
        #   img: 结果存入这个变量
        cv2.addWeighted(inverse_mask, opacity, img, 1, 0, img)

    def _get_roi_coordinates(self) -> Tuple[int, int, int, int]:
        """
        获取标准化后的区域坐标

        这个方法计算最终的区域坐标

        处理的情况:
            1. 用户可能从右下角向左上角拖拽
               需要交换起始点和结束点
            2. 计算区域的宽度和高度
            3. 确保坐标是有效的（非负）

        返回值:
            (x, y, width, height) 四元组
        """
        # 计算起始坐标
        # 使用 min() 确保 x_start 是较小的值
        x_start = min(self.coords["ix"], self.coords["x_end"])
        y_start = min(self.coords["iy"], self.coords["y_end"])

        # 计算宽度和高度
        # 使用 abs() 取绝对值
        width = abs(self.coords["x_end"] - self.coords["ix"])
        height = abs(self.coords["y_end"] - self.coords["iy"])

        # 返回标准化的坐标
        return (x_start, y_start, width, height)
