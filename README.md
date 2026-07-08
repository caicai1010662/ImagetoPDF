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
python .\gui.py
```

如果提示缺少 Pillow，请执行：

```powershell
python -m pip install Pillow
```

## 分享给别人

如果只分享软件本体，建议发送这些文件：

- `gui.py`
- `gui_preview.py`
- `gui_pagetable.py`
- `theme.py`
- `imgtopdf.py`
- `converter.py`
- `image_files.py`
- `image_encoder.py`
- `pdf_writer.py`
- `start_gui.bat`
- `README.md`

对方电脑需要安装 Python 3 和 Pillow。若想让对方无需安装 Python，可以后续打包成 `.exe`。

## 项目结构

- `gui.py`：桌面界面入口。
- `gui_preview.py`：缩略图预览面板组件。
- `gui_pagetable.py`：页面列表表格组件。
- `theme.py`：配色与 Ttk 样式配置。
- `imgtopdf.py`：命令行入口。
- `converter.py`：图片转 PDF 的主流程。
- `image_files.py`：图片文件发现、排序和元数据提取。
- `image_encoder.py`：PDF 图像流编码器。
- `pdf_writer.py`：底层 PDF 对象写入。

## 命令行备用

界面是推荐入口。若需要命令行转换，也可以使用：

```powershell
python .\imgtopdf.py .\IMG\1 .\output\pdf\document-1.pdf --auto-orient
```
