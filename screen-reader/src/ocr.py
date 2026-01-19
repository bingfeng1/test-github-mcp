# -*- coding: utf-8 -*-
"""
=================================================================
OCR 文字识别模块 (Optical Character Recognition Module)
=================================================================

功能说明:
    这个模块负责从图片中识别出文字
    使用 Tesseract OCR 引擎进行文字识别

核心类:
    OCREngine - OCR 引擎

工作原理:
    1. 截取屏幕指定区域的图片
    2. 将图片交给 Tesseract 引擎识别
    3. Tesseract 分析图片中的文字形状
    4. 返回识别出的文字字符串

OCR 是什么？
    OCR (Optical Character Recognition) = 光学字符识别
    简单说：让电脑"看懂"图片中的文字
    就像我们用眼睛读书一样，OCR 让电脑也能"阅读"图片

Tesseract 是什么？
    Tesseract 是一个开源的 OCR 引擎
    由 Google 维护和支持
    可以识别很多种语言的文字
    我们使用中文语言包（chi_tra，因为简体中文包有时不太稳定）

依赖说明:
    - pytesseract: Python 封装层，让 Python 可以调用 Tesseract
    - Pillow (PIL): Python 图片处理库，用于读取和管理图片
    - pyautogui: 屏幕截图库，用于截取屏幕区域
=================================================================
"""

# ======================
# 导入必要的模块
# ======================

# os: 操作系统模块
# 用于检查文件是否存在、判断操作系统类型
import os

# PIL (Pillow): Python 图片处理库
# PIL = Python Imaging Library
# Pillow 是 PIL 的现代维护版本
# 提供了丰富的图片处理功能
from PIL import Image

# pytesseract: Tesseract OCR 的 Python 封装
# 让我们可以用 Python 代码调用 Tesseract 引擎
import pytesseract

# typing: 类型提示模块
# 用于声明函数参数和返回值的类型
from typing import Tuple, Optional


class OCREngine:
    """
    OCR 引擎

    这个类是整个 OCR 模块的核心

    主要功能:
        1. 配置 Tesseract 引擎路径
        2. 截取屏幕指定区域的图片
        3. 使用 Tesseract 识别图片中的文字
        4. 清理和返回识别结果

    使用示例:
        # 创建引擎
        ocr = OCREngine()

        # 截取并识别文字
        region = (100, 100, 500, 200)  # x, y, width, height
        text = ocr.extract_from_region(region)

        # 打印识别结果
        print(text)
    """

    def __init__(self, tesseract_path: Optional[str] = None):
        """
        初始化 OCR 引擎

        参数说明:
            tesseract_path: Tesseract 可执行文件的完整路径
                            例如: r"C:\Program Files\Tesseract-OCR\tesseract.exe"
                            如果是 None，会使用默认路径

        初始化时会:
            1. 保存 Tesseract 路径
            2. 调用 _configure_tesseract() 配置引擎
        """
        # 调用配置方法，设置 Tesseract 的路径
        self._configure_tesseract(tesseract_path)

    def _configure_tesseract(self, tesseract_path: Optional[str] = None) -> None:
        """
        配置 Tesseract 路径

        这个方法负责找到并配置 Tesseract 引擎

        工作流程:
            1. 如果没有指定路径，使用默认路径
            2. 检查 Tesseract 是否存在
            3. 如果存在，配置 pytesseract 使用这个路径
            4. 如果不存在，抛出错误提示用户安装

        默认路径说明:
            - Windows: C:\Program Files\Tesseract-OCR\tesseract.exe
            - Linux/Mac: /usr/bin/tesseract
        """
        # 检查是否指定了路径
        if tesseract_path is None:
            # 没有指定，使用默认路径

            # 判断操作系统类型
            # os.name 的值:
            #   - "nt" = Windows
            #   - "posix" = Linux/Mac
            if os.name == "nt":
                # Windows 系统
                # 使用原始字符串 (r"...") 避免转义问题
                # 默认路径: C:\Program Files\Tesseract-OCR\tesseract.exe
                tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            else:
                # Linux/Mac 系统
                # 默认路径: /usr/bin/tesseract
                tesseract_path = "/usr/bin/tesseract"

        # 检查 Tesseract 是否存在
        # os.path.exists() 检查文件或目录是否存在
        if os.path.exists(tesseract_path):
            # Tesseract 存在，配置 pytesseract 使用这个路径
            # pytesseract.pytesseract.tesseract_cmd 是 Tesseract 的可执行文件路径
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            # Tesseract 不存在，抛出错误
            # FileNotFoundError 是 Python 内置异常，表示文件未找到
            raise FileNotFoundError(
                f"Tesseract 未找到: {tesseract_path}\n"
                "请从 https://github.com/UB-Mannheim/tesseract/wiki 下载安装"
            )

    def capture_region(self, region: Tuple[int, int, int, int]) -> Image.Image:
        """
        截取屏幕指定区域

        这个方法使用 pyautogui 库截取屏幕的指定区域

        参数说明:
            region: 区域坐标，格式为 (x, y, width, height)
                    x: 区域左上角的 X 坐标（水平位置）
                    y: 区域左上角的 Y 坐标（垂直位置）
                    width: 区域的宽度（像素）
                    height: 区域的高度（像素）

        返回值:
            PIL Image 对象
            包含截取区域的图片

        使用示例:
            # 截取屏幕左上角 100x100 像素的区域
            region = (0, 0, 100, 100)
            image = ocr.capture_region(region)

        pyautogui 是什么？
            pyautogui 是一个控制鼠标和键盘的 Python 库
            也可以用来截取屏幕截图
            screenshot() 方法可以截取整个屏幕或指定区域
        """
        # 导入 pyautogui 模块
        # 在函数内部导入可以避免在文件开头产生依赖
        import pyautogui

        # 截取屏幕区域
        # pyautogui.screenshot() 的参数 region 是一个四元组
        # (x, y, width, height)
        screenshot = pyautogui.screenshot(region=region)

        # 返回截取的图片
        return screenshot

    def recognize_text(self, image: Image.Image, lang: str = "chi_tra+eng") -> str:
        """
        识别图片中的文字

        这个方法使用 Tesseract 引擎从图片中提取文字

        参数说明:
            image: PIL Image 对象，包含要识别的图片
            lang: 语言代码，用于指定识别哪些语言
                  "chi_tra" = 繁体中文
                  "chi_sim" = 简体中文（有时不太稳定）
                  "eng" = 英文
                  可以组合使用，如 "chi_tra+eng" 同时识别中文和英文

        返回值:
            识别出的文字字符串
            如果图片中没有文字，返回空字符串

        Tesseract 配置参数说明:
            --psm 6:
                PSM = Page Segmentation Mode（页面分割模式）
                6 = 假设有一个统一的文本块
                适合识别连续的文本段落
                其他模式:
                  0 = 定向脚本分析
                  1 = 自动页面分割，带有 OSD
                  2 = 自动页面分割，不带 OSD
                  3 = 完全自动页面分割，但不使用 OSD
                  4 = 假设一列可变大小文字
                  5 = 假设一列统一大小的文字
                  6 = 假设有一个统一的文本块 ← 我们用的
                  7 = 把图片当作单个文字行处理
                  8 = 把图片当作单个单词处理
                  9 = 把图片当作单个单词的圆圈处理
                  10 = 把图片当作单个字符处理
                  11 = 稀疏文字，按列查找
                  12 = 稀疏文字，按页查找
                  13 = 按行处理

            --oem 3:
                OEM = OCR Engine Mode（OCR 引擎模式）
                3 = 使用 LSTM 神经网络引擎（最准确）
                其他模式:
                  0 = 传统 Tesseract - 仅传统引擎
                  1 = 神经网络 LSTM 引擎仅
                  2 = 传统 + LSTM 引擎
                  3 = 默认，使用可用的引擎 ← 我们用的

            -c preserve_interword_spaces=1:
                保留词之间的空格
                1 = 启用，0 = 禁用
        """
        # 构建 Tesseract 配置字符串
        # 这些参数告诉 Tesseract 如何处理图片
        config = "--psm 6 --oem 3 -c preserve_interword_spaces=1"

        # 调用 Tesseract 识别文字
        # pytesseract.image_to_string() 是主要函数
        # 参数:
        #   image: 要识别的图片
        #   lang: 语言代码
        #   config: 配置参数
        text = pytesseract.image_to_string(image, lang=lang, config=config)

        # 清理识别结果
        # ======================

        # 1. 按换行符分割成行
        # 2. 对每行去除首尾空白
        # 3. 过滤掉空行
        # 4. 重新用换行符连接

        # text.split('\n') 按换行符分割，得到一个列表
        # [line.strip() for line in ...] 对每行应用 strip()，去除首尾空白
        # if line.strip() 过滤掉空白行
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # '\n'.join(lines) 用换行符把行连接起来
        text = '\n'.join(lines)

        # 返回清理后的结果
        return text

    def extract_from_region(self, region: Tuple[int, int, int, int]) -> str:
        """
        从指定区域捕获并识别文字

        这是最常用的方法，一站式完成截图和识别

        参数说明:
            region: 区域坐标，格式为 (x, y, width, height)
                    x: 左上角 X 坐标
                    y: 左上角 Y 坐标
                    width: 宽度
                    height: 高度

        返回值:
            识别出的文字字符串

        工作流程:
            1. 调用 capture_region() 截取指定区域的图片
            2. 调用 recognize_text() 识别图片中的文字
            3. 返回识别结果

        使用示例:
            # 识别屏幕某个区域的文字
            region = (100, 100, 400, 300)
            text = ocr.extract_from_region(region)
            print(text)
        """
        # 第一步：截取区域图片
        image = self.capture_region(region)

        # 第二步：识别图片中的文字
        return self.recognize_text(image)

    def get_text_diff(self, old_text: str, new_text: str) -> str:
        """
        获取新增的文本部分

        这个方法用于比较两次识别结果，找出新增的内容

        用途:
            在屏幕阅读场景中，我们只关心新出现的内容
            这个方法帮助找出两次识别之间的差异

        参数说明:
            old_text: 上一次的识别结果（旧的文本）
            new_text: 当前的识别结果（新的文本）

        返回值:
            新增的文本部分

        逻辑说明:
            1. 如果新文本为空，返回空字符串
            2. 如果旧文本为空，返回整个新文本
            3. 如果新文本以旧文本开头，返回新增的部分
            4. 否则（内容完全不同），返回整个新文本

        使用示例:
            old = "今天天气"
            new = "今天天气真好"
            diff = ocr.get_text_diff(old, new)
            # diff = "真好"

            old = "hello"
            new = "world"
            diff = ocr.get_text_diff(old, new)
            # diff = "world"（因为内容完全不同）
        """
        # 检查新文本是否为空
        if not new_text:
            # 新文本为空，没有新增内容
            return ""

        # 检查旧文本是否为空
        if not old_text:
            # 旧文本为空，全部都是新的
            return new_text

        # 检查新文本是否以旧文本开头
        if new_text.startswith(old_text):
            # 新文本是旧文本的扩展
            # 新增部分 = 新文本 - 旧文本
            # 例如:
            #   old_text = "今天天气"
            #   new_text = "今天天气真好"
            #   新增 = "真好"
            return new_text[len(old_text):].strip()
        else:
            # 内容完全不同，返回整个新文本
            # 这种情况可能是因为区域内容发生了重大变化
            return new_text
