# Screen Reader

屏幕区域文字提取和语音播报工具，类似于直播中的聊天信息抓取。

## 功能

- 划出屏幕指定区域
- 自动读取选定区域的文字（OCR）
- 实时语音播报新增内容
- 只播报最新一条信息

## 安装

### 1. 安装 Python 依赖

```bash
# 使用 Poetry（推荐）
poetry install

# 或使用 pip
pip install -r requirements.txt
```

### 2. 安装 Tesseract OCR

**Windows:**
1. 下载地址：https://github.com/UB-Mannheim/tesseract/wiki
2. 安装后添加到系统环境变量，或在运行指定路径：
   ```python
   reader = ScreenReader(tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe")
   ```

**Linux:**
```bash
sudo apt install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

## 使用方法

```bash
# 运行程序
python src/main.py

# 或指定检查间隔
python src/main.py -i 0.5  # 0.5秒检查一次

# 或指定 Tesseract 路径
python src/main.py -t "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## 操作说明

1. 运行程序后，会弹出全屏窗口
2. 拖拽鼠标选择要监控的区域
3. 按 `Enter` 或 `C` 确认选择
4. 按 `Esc` 取消退出
5. 开始监控选区，检测到新内容会自动语音播报
6. 按 `Ctrl+C` 停止程序

## 项目结构

```
screen-reader/
├── pyproject.toml      # Poetry 项目配置
├── requirements.txt    # pip 依赖列表
├── src/
│   ├── __init__.py
│   ├── selector.py     # 区域选择模块
│   ├── ocr.py          # OCR 文字识别模块
│   ├── tts.py          # 语音播报模块
│   └── main.py         # 主程序入口
└── README.md
```

## 依赖说明

| 包名 | 用途 |
|------|------|
| pyautogui | 屏幕截图、鼠标控制 |
| pytesseract | OCR 文字识别 |
| pyttsx3 | 文字转语音 |
| Pillow | 图片处理 |
| opencv-python | 图像显示、区域选择 |
| numpy | 数组处理 |
