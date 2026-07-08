# 图片转 PDF 工具

一个轻量、无损的图片转 PDF 桌面工具。

## 功能

- 支持常见图片：JPG、JPEG、PNG、BMP、GIF、TIFF、WEBP。
- 无损转换：JPG/JPEG 直接嵌入原始数据；其他格式使用无损像素压缩写入 PDF。
- 多选载入：通过系统文件选择器选择图片文件，可看到图片文件和缩略图。
- 逐页预览：导出前可以检查每一页方向和顺序。
- 逐页旋转：支持单页左旋、右旋。
- 批量处理：支持按照片 EXIF 方向自动修正、全部归零。
- 页面管理：支持上移、下移、从本次导出中移除页面。
- 中文界面：按钮、提示、错误信息均为中文。

## 启动方式

双击：

```powershell
.\start_gui.bat
```

或者手动运行：

```powershell
python .\main.py
```

如果提示缺少 Pillow，请执行：

```powershell
python -m pip install Pillow
```

## 分享给别人

如果只分享软件本体，建议发送这些文件：

- `main.py`
- `imgtopdf.py`
- `img2pdf/`
- `gui/`
- `start_gui.bat`
- `README.md`

对方电脑需要安装 Python 3 和 Pillow。若想让对方无需安装 Python，可以后续打包成 `.exe`。

## 项目结构

```
├── main.py              # 桌面界面启动入口
├── imgtopdf.py          # 命令行启动入口
├── start_gui.bat        # Windows 一键启动脚本
├── requirements.txt
│
├── img2pdf/             # 核心库（无界面依赖）
│   ├── converter.py     # 图片转 PDF 主流程
│   ├── files.py         # 图片文件发现、排序、元数据
│   ├── encoder.py       # PDF 图像流编码器
│   └── writer.py        # 底层 PDF 对象写入
│
└── gui/                 # 桌面界面组件
    ├── app.py           # 主窗口应用
    ├── preview.py       # 缩略图预览面板
    ├── pagetable.py     # 页面列表表格
    └── theme.py         # 配色与样式配置
```

## 命令行备用

界面是推荐入口。若需要命令行转换，也可以使用：

```powershell
python .\imgtopdf.py .\IMG\1 .\output\pdf\document-1.pdf --auto-orient
```
