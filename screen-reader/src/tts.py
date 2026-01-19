# -*- coding: utf-8 -*-
"""
=================================================================
语音播报模块 (Text-to-Speech Module)
=================================================================

功能说明:
    这个模块负责把文字转换成语音并播放出来
    使用 Windows 系统自带的语音引擎 (SAPI)

核心类:
    TTSPlayer - 文字转语音播放器

工作原理:
    1. 当需要播报文字时，调用 speak() 方法
    2. speak() 会把文字加入到一个"等待播报的队列"中
    3. 后台有一个一直在运行的"播报线程"
    4. 播报线程从队列中取出文字，一个一个地播放
    5. 这样即使同时有多条消息，也能按顺序全部播报出来

依赖说明:
    - win32com.client: Windows COM 组件，用于调用系统语音引擎
    - pythoncom: Python 的 COM 库，处理 Windows 组件通信
    - threading: 线程模块，让播报在后台运行，不阻塞主程序
=================================================================
"""

# 导入必要的模块
# ==============

# win32com.client: Windows 的 COM 组件调用工具
# 有了它，Python 就能调用 Windows 自带的程序，比如语音合成
import win32com.client

# pythoncom: Python 的 COM 运行环境
# Windows 的 COM 组件需要在特定的线程环境中运行，这个模块提供支持
import pythoncom

# threading: 线程模块
# 线程就像是一条独立的工作流水线，可以让播报和监控同时进行
import threading


class TTSPlayer:
    """
    文字转语音播放器

    这个类的主要作用：
    1. 初始化语音引擎
    2. 接收要播报的文字
    3. 把文字加入到播报队列
    4. 后台线程按顺序播报队列中的内容
    """

    def __init__(self, rate: int = 100, volume: float = 1.0):
        """
        初始化 TTS 播放器

        参数说明:
            rate: 语速，数值越大越快
                  -10 最慢，10 最快
                  这里的 100 会被转换成 SAPI 的 -5（适中偏慢）
                  默认值 100
            volume: 音量，范围 0.0 到 1.0
                    1.0 是最大音量
                    默认值 1.0

        初始化时会发生:
            1. 保存语速和音量设置
            2. 创建一个空的播报队列（用来存放待播报的消息）
            3. 创建线程锁（防止多线程同时操作队列导致出错）
            4. 设置运行标志为 True
            5. 启动后台播报线程
        """
        # 语速设置
        self.rate = rate

        # 音量设置
        self.volume = volume

        # 播报队列：用来存放等待播报的文字
        # 列表中的每一项就是要播报的一句话
        self._queue = []

        # 线程锁：保护队列的互斥锁
        # 当一个线程在操作队列时，其他线程必须等待
        # 这样保证队列数据不会混乱
        self._lock = threading.Lock()

        # 运行标志：控制播报线程是否继续运行
        # True = 继续运行，False = 停止
        self._running = True

        # 播报线程对象
        self._thread = None

        # 启动后台播报线程
        # 这一步会让播报线程开始工作，不断检查队列
        self._start_thread()

    def _start_thread(self):
        """
        启动后台播报线程

        这个方法创建一个新线程，专门负责播报文字

        线程是什么？
            想象一个工厂有一条主生产线（主程序）
            现在再建一条辅助生产线（后台线程）
            主生产线负责监控屏幕、识别文字
            辅助生产线专门负责播报语音
            两条线同时工作，互不干扰
        """
        # 创建线程对象
        # target=self._speak_thread 表示这个线程要执行 _speak_thread 方法
        # daemon=True 表示主程序结束时，这个线程也会自动结束
        self._thread = threading.Thread(target=self._speak_thread, daemon=True)

        # 启动线程
        # 调用 start() 后，线程就开始执行 _speak_thread 方法了
        self._thread.start()

        # 打印日志，告诉用户线程已启动
        print("[TTS] 后台线程已启动")

    def _init_voice(self):
        """
        初始化语音引擎

        这个方法创建一个 Windows 语音对象，并设置语速和音量

        返回值:
            voice: 配置好的语音对象，可以用来播报文字

        SAPI 是什么？
            SAPI (Speech Application Programming Interface)
            是 Windows 自带的语音编程接口
            我们不需要安装额外软件，直接调用系统功能
        """
        # 初始化 COM 组件运行环境
        # 在 Windows 中，COM 组件需要在特定的线程环境中运行
        # 每次在新线程中使用 COM 组件前，都需要调用这个
        pythoncom.CoInitialize()

        # 创建语音对象
        # Dispatch 就像是一个"召唤"操作
        # "SAPI.SpVoice" 是 Windows 语音引擎的组件名
        voice = win32com.client.Dispatch("SAPI.SpVoice")

        # 设置语速
        # SAPI 的语速范围是 -10 到 10
        # 我们把 100 转换成 -5 (100 - 50 = -5)
        voice.Rate = self.rate - 50

        # 设置音量
        # SAPI 的音量范围是 0 到 100
        # 我们的 volume 是 0.0 到 1.0，所以乘以 100
        voice.Volume = int(self.volume * 100)

        # 返回配置好的语音对象
        return voice

    def _speak_thread(self):
        """
        播报线程 - 持续运行，播报队列中的所有内容

        这个方法在线程中运行，流程是：
        1. 检查队列是否有待播报的内容
        2. 如果有，取出第一条，播放语音
        3. 如果没有，等待一小会儿后继续检查
        4. 重复直到 _running 变为 False

        这是一个无限循环，只要 _running 为 True 就会一直运行
        """
        # 打印日志，告诉用户播报线程开始工作了
        print("[TTS] 播报线程已启动")

        # 初始化 COM 环境（在新线程中必须这样做）
        pythoncom.CoInitialize()

        # 只要运行标志为 True，就继续循环
        while self._running:

            # 从队列中取出待播报的内容
            # ======================

            # 加锁：防止其他线程同时操作队列
            # with 语句会自动加锁和解锁
            with self._lock:

                # 检查队列是否为空
                if self._queue:
                    # 队列不为空，取出第一条消息
                    # pop(0) 取出列表第一个元素，并从列表中删除
                    text = self._queue.pop(0)

                    # 打印日志：显示取出的内容（只显示前20个字符）
                    print(f"[TTS] 取出待播报内容: {text[:20]}...")
                else:
                    # 队列为空，没有要播报的内容
                    text = None

            # ======================
            # 解锁自动发生，队列操作完成

            # 检查是否有内容需要播报
            if text:
                # 有内容，播放语音
                # ======================
                try:
                    # 创建语音对象
                    voice = self._init_voice()

                    # 遍历系统中所有可用的语音
                    # GetVoices() 返回所有已安装的语音列表
                    for v in voice.GetVoices():
                        # 获取当前语音的名称
                        name = v.GetAttribute("Name")

                        # 打印日志：显示发现的语音名称
                        print(f"[TTS] 发现语音: {name}")

                        # 检查是否是中文语音
                        # Huihui 是微软的中文女声
                        # Xiaoxiao 是微软的中文语音（较新版本）
                        # Chinese 表示包含中文
                        if "Huihui" in name or "Xiaoxiao" in name or "Chinese" in name:
                            # 选择这个语音
                            voice.Voice = v

                            # 打印日志
                            print(f"[TTS] 选择语音: {name}")
                            # 找到一个合适的就停止搜索
                            break

                    # 开始播报
                    # Speak() 是同步方法，会阻塞直到播报完成
                    voice.Speak(text)

                    # 打印日志：播报完成
                    print(f"[TTS] 播报完成")

                except Exception as e:
                    # 如果播放过程中出错，打印错误信息
                    # 这样我们能看到具体是什么问题
                    print(f"[TTS 错误] {e}")

            else:
                # 队列为空，没有内容要播报
                # 等待 0.1 秒后继续检查队列
                # 这样做可以避免 CPU 被这个线程占满

                # 导入 time 模块（这里导入是为了避免全局依赖）
                import time

                # 休眠 0.1 秒
                time.sleep(0.1)

        # 循环结束（_running 变为 False）
        print("[TTS] 播报线程已退出")

    def speak(self, text: str) -> None:
        """
        播报文字

        这个方法是给外部调用的接口
        主程序检测到新内容后，调用这个方法把内容加入播报队列

        参数说明:
            text: 要播报的文字内容

        工作流程:
            1. 检查文字是否为空
            2. 去除首尾空白字符
            3. 加锁
            4. 把文字加入队列
            5. 解锁
        """
        # 检查文字是否为空
        if not text:
            return

        # 去除首尾空白（空格、换行等）
        text = text.strip()

        # 再次检查是否为空（去除空白后可能变成空字符串）
        if not text:
            return

        # 加锁，保护队列
        with self._lock:

            # 把文字加入到队列末尾
            self._queue.append(text)

            # 打印日志：显示当前队列中有多少条消息
            print(f"[TTS] 添加到队列，当前队列长度: {len(self._queue)}")

        # 解锁自动发生

    def stop(self) -> None:
        """
        停止播报

        这个方法用于完全停止播报功能
        通常在程序退出时调用

        工作流程:
            1. 设置运行标志为 False（让播报线程退出循环）
            2. 清空队列（不播报排队中的消息）
            3. 尝试强制停止当前正在播放的语音
        """
        # 设置运行标志为 False
        # 这会让播报线程的 while 循环结束
        self._running = False

        # 加锁，清空队列
        with self._lock:
            self._queue.clear()

        # 尝试强制停止当前语音
        try:
            # 初始化 COM
            pythoncom.CoInitialize()

            # 创建语音对象
            voice = win32com.client.Dispatch("SAPI.SpVoice")

            # 播放空内容，并设置停止标志
            # 3 = SVSFPurgeBeforeSpeak 表示停止当前播报
            voice.Speak("", 3)
        except:
            # 如果出错就忽略（因为程序可能正在退出）
            pass

    def get_available_voices(self) -> list:
        """
        获取系统中所有可用的语音列表

        返回值:
            一个列表，每个元素是一个字典，包含语音信息：
            - name: 语音名称
            - age: 语音年龄
            - gender: 语音性别
            - language: 支持的语言

        使用示例:
            voices = tts.get_available_voices()
            for v in voices:
                print(v['name'])
        """
        try:
            # 初始化 COM
            pythoncom.CoInitialize()

            # 创建语音对象
            voice = win32com.client.Dispatch("SAPI.SpVoice")

            # 存储结果的列表
            voices = []

            # 遍历所有可用语音
            for v in voice.GetVoices():
                # 获取语音的各个属性
                voices.append({
                    "name": v.GetAttribute("Name"),       # 名称
                    "age": v.GetAttribute("Age"),         # 年龄
                    "gender": v.GetAttribute("Gender"),   # 性别
                    "language": v.GetAttribute("Language"), # 语言
                })

            # 返回语音列表
            return voices

        except Exception as e:
            # 获取失败时打印错误，返回空列表
            print(f"[错误] 获取语音列表失败: {e}")
            return []
