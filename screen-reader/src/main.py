# -*- coding: utf-8 -*-
"""
=================================================================
主程序入口 (Main Program Entry Point)
=================================================================

功能说明:
    这是整个屏幕阅读器程序的主入口
    负责协调区域选择、文字识别和语音播报

工作流程:
    1. 程序启动，初始化各个模块
    2. 让用户选择要监控的屏幕区域
    3. 进入监控循环：
       a. 截取指定区域的图片
       b. 使用 OCR 识别图片中的文字
       c. 检测是否有新内容
       d. 如果有新内容，加入播报队列
       e. 等待一段时间后重复
    4. 用户按 Ctrl+C 退出程序

核心类:
    ScreenReader - 屏幕阅读器主类

依赖模块:
    - selector: 区域选择模块
    - ocr: 文字识别模块
    - tts: 语音播报模块
=================================================================
"""

# 导入系统模块
# ==============

# sys: Python 系统模块
# 用于访问系统相关的功能和变量
import sys

# os: 操作系统模块
# 用于处理文件路径、目录等操作系统相关功能
import os

# time: 时间模块
# 用于实现延时等待
import time

# typing: 类型提示模块
# 用于声明变量类型，让代码更清晰
from typing import Optional, Tuple


# ======================
# 程序编码配置
# ======================

# 设置 UTF-8 编码输出
# Windows 控制台默认使用 GBK 编码，可能会导致中文显示乱码
# 这两行代码确保控制台正确显示 UTF-8 字符
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')


# ======================
# 添加 src 目录到 Python 路径
# ======================

# 获取当前文件的完整路径
# __file__ 是 Python 内置变量，表示当前文件的名字
# os.path.abspath() 把相对路径转成绝对路径
# os.path.dirname() 获取目录部分
current_dir = os.path.dirname(os.path.abspath(__file__))

# 把 src 目录添加到 Python 的模块搜索路径
# 这样就可以直接 import selector、ocr、tts 这些模块了
sys.path.insert(0, current_dir)


# ======================
# 导入自定义模块
# ======================

# 区域选择模块：负责让用户选择屏幕区域
from selector import RegionSelector

# OCR 文字识别模块：负责从图片中提取文字
from ocr import OCREngine

# 语音播报模块：负责把文字转换成语音播放
from tts import TTSPlayer


class ScreenReader:
    """
    屏幕阅读器主类

    这个类是整个程序的核心，协调各个模块的工作

    主要功能:
        1. 管理用户选择的屏幕区域
        2. 定期截取区域图片
        3. 使用 OCR 识别文字
        4. 检测新内容并触发语音播报

    工作流程:
        初始化 -> 选择区域 -> 开始监控 -> (截取 -> 识别 -> 播报) 循环 -> 退出
    """

    def __init__(self, check_interval: float = 0.5, tesseract_path: Optional[str] = None):
        """
        初始化屏幕阅读器

        参数说明:
            check_interval: 检查间隔时间，单位是秒
                            默认值 0.5 秒
                            每隔这么多时间检查一次屏幕
            tesseract_path: Tesseract OCR 引擎的可执行文件路径
                            如果是 None，会使用默认路径

        初始化时会创建三个核心组件:
            1. RegionSelector - 区域选择器
            2. OCREngine - OCR 文字识别引擎
            3. TTSPlayer - 语音播报器
        """
        # 区域选择器
        # 负责让用户用鼠标选择要监控的屏幕区域
        self.selector = RegionSelector()

        # OCR 引擎
        # 负责从图片中识别文字
        # tesseract_path 参数指定 Tesseract 程序的位置
        self.ocr = OCREngine(tesseract_path)

        # 语音播报器
        # 负责把文字转换成语音播放
        # rate=100 是语速（较慢）
        # volume=0.9 是音量（90%）
        self.tts = TTSPlayer(rate=100, volume=0.9)

        # 检查间隔
        # 每隔这么多秒检查一次屏幕
        self.check_interval = check_interval

        # 当前选中的区域
        # 格式: (x, y, width, height)
        # x, y: 区域左上角的坐标
        # width, height: 区域的宽度和高度
        # None 表示还没有选择区域
        self.region: Optional[Tuple[int, int, int, int]] = None

        # 上一次识别到的完整文本
        # 用于检测是否有新内容
        # 初始化为空字符串
        self.last_text = ""

        # 程序运行状态
        # True = 正在运行，False = 已停止
        self.is_running = False

    def select_region(self) -> bool:
        """
        让用户选择要监控的屏幕区域

        这个方法会:
            1. 显示提示信息，告诉用户如何操作
            2. 弹出一个全屏窗口
            3. 等待用户用鼠标拖拽选择区域
            4. 返回用户选择的区域坐标

        返回值:
            bool 类型
            - True: 成功选择了区域
            - False: 用户取消了选择（按了 Esc）
        """
        # 打印提示信息
        print("请拖拽鼠标选择要监控的区域...")
        print("按 Enter 或 C 确认，按 Esc 退出")

        # 调用选择器，让用户选择区域
        # select_region() 方法会弹出一个全屏窗口
        # 用户拖拽完成后，返回区域坐标
        region = self.selector.select_region()

        # 检查是否成功选择
        if region is None:
            # 用户取消了选择
            print("已取消选择")
            return False

        # 保存选中的区域
        self.region = region

        # 打印选中的区域信息
        print(f"已选择区域: {region}")
        return True

    def run(self) -> None:
        """
        运行监控循环

        这是程序的核心方法，负责持续监控屏幕

        工作流程:
            1. 确保已选择区域（如果没有，调用 select_region）
            2. 打印开始信息
            3. 进入循环：
               a. 截取指定区域的图片
               b. 使用 OCR 识别文字
               c. 检测是否有新内容
               d. 如果有新内容，加入播报队列
               e. 等待一段时间
            4. 响应 Ctrl+C 中断
        """
        # 检查是否已选择区域
        if self.region is None:
            # 还没有选择区域，让用户选择
            if not self.select_region():
                # 用户取消选择，退出
                return

        # 打印分隔线，看起来更整齐
        print("\n" + "=" * 50)

        # 打印开始信息
        print("开始监控区域...")
        print("检测到新内容会自动播报（会排队）")
        print("按 Ctrl+C 停止")

        # 打印分隔线
        print("=" * 50 + "\n")

        # 设置运行状态为 True
        self.is_running = True

        try:
            # ======================
            # 主监控循环
            # ======================

            # 只要 is_running 是 True，就继续循环
            while self.is_running:

                # ----------------------
                # 第一步：截取并识别文字
                # ----------------------

                # 调用 OCR 引擎，从指定区域提取文字
                # self.region 是用户选择的区域坐标
                # 返回值是识别出的文字（字符串）
                text = self.ocr.extract_from_region(self.region)

                # ----------------------
                # 第二步：处理识别结果
                # ----------------------

                # 检查是否识别到文字
                if text:
                    # 规范化文本
                    # 1. 移除所有空格（OCR 可能会在字之间加空格）
                    # 2. 移除首尾空白
                    text = text.replace(' ', '').strip()

                    # 打印日志：显示识别到了多少字符
                    print(f"[监控] 识别到 {len(text)} 字符")

                    # ----------------------
                    # 第三步：检测新内容
                    # ----------------------

                    # 检查文字是否有变化
                    if text and text != self.last_text:
                        # 文字变了！

                        # 判断是首次识别还是增量更新
                        if not self.last_text:
                            # 第一次识别，没有任何历史内容
                            # 播报全部内容
                            new_content = text

                            # 打印日志
                            print(f"[首次] 播报全部内容")

                        else:
                            # 不是第一次，有历史内容
                            # 计算新增的部分
                            # new_text = "旧内容" + "新内容"
                            # 所以新内容 = 完整内容 - 旧内容
                            new_content = text[len(self.last_text):].strip()

                            # 打印日志：显示新增内容的长度
                            print(f"[增量] 新增内容长度: {len(new_content)}")

                        # ----------------------
                        # 第四步：触发语音播报
                        # ----------------------

                        # 检查新增内容是否有效
                        # 至少要有 2 个字符才播报，避免噪音
                        if new_content and len(new_content) >= 2:
                            # 打印新内容（只显示前 30 个字符）
                            print(f"[新内容] {new_content[:30]}...")

                            # 调用语音播报器，把新内容加入队列
                            self.tts.speak(new_content)
                        else:
                            # 内容太短，可能是误识别
                            print(f"[跳过] 内容太短或为空")

                        # 更新历史记录
                        # 保存当前的完整内容，作为下一次比较的基础
                        self.last_text = text

                    else:
                        # 文字没有变化
                        print(f"[相同] 内容无变化")

                # ----------------------
                # 第五步：等待下一次检查
                # ----------------------

                # 等待一段时间再检查
                # 这样可以避免 CPU 占用过高
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            # 用户按了 Ctrl+C，触发这个异常
            print("\n正在停止...")

        except Exception as e:
            # 发生其他错误
            print(f"\n发生错误: {e}")

        finally:
            # 无论是否发生异常，都会执行这里
            # 确保程序正确停止
            self.stop()

    def stop(self) -> None:
        """
        停止监控

        这个方法用于优雅地停止程序

        工作流程:
            1. 设置运行状态为 False（让循环结束）
            2. 停止语音播报
            3. 打印停止信息
        """
        # 设置运行状态为 False
        # 这会让主循环的 while 条件不满足，从而退出循环
        self.is_running = False

        # 停止语音播报
        # 会清空播报队列，并尝试停止当前正在播放的语音
        self.tts.stop()

        # 打印停止信息
        print("已停止")


def main():
    """
    主函数 - 程序入口点

    这个函数是程序的起点
    Python 脚本运行时，会从这里的代码开始执行

    工作流程:
        1. 解析命令行参数
        2. 创建 ScreenReader 对象
        3. 让用户选择区域
        4. 开始监控
    """
    # 导入 argparse 模块（用于解析命令行参数）
    import argparse

    # 创建参数解析器
    # description 是帮助信息的描述
    parser = argparse.ArgumentParser(description="屏幕区域文字提取和语音播报工具")

    # 添加命令行参数
    # -i, --interval: 检查间隔
    # type=float 表示参数值要转换成浮点数
    # default=0.5 表示默认值是 0.5
    # help 是帮助信息
    parser.add_argument("-i", "--interval", type=float, default=0.5,
                        help="检查间隔（秒），默认0.5秒")

    # -t, --tesseract: Tesseract 路径
    parser.add_argument("-t", "--tesseract", type=str, default=None,
                        help="Tesseract 可执行文件路径")

    # 解析命令行参数
    # 解析后的参数存储在 args 对象中
    args = parser.parse_args()

    # 创建屏幕阅读器对象
    # 传入检查间隔和 Tesseract 路径
    reader = ScreenReader(check_interval=args.interval, tesseract_path=args.tesseract)

    # 让用户选择要监控的区域
    # 如果用户取消选择，直接退出程序
    if not reader.select_region():
        # 退出程序，返回码 0 表示正常退出
        sys.exit(0)

    # 开始监控
    reader.run()


# ======================
# 程序入口点
# ======================

# if __name__ == "__main__": 是 Python 特有的写法
# 表示只有直接运行这个脚本时，才会执行下面的代码
# 如果其他脚本 import 这个文件，下面的代码不会执行

# 这是一种常见的 Python 最佳实践：
# - 让模块既可以直接运行，也可以被其他模块导入
if __name__ == "__main__":
    # 调用 main() 函数，开始执行程序
    main()
