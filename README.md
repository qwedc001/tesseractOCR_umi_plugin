<h1 align="center">适用于 Umi-OCR 文字识别工具 的 Tesseract 插件</h1>

<p align="center">
  <a href="https://github.com/hiroi-sora/Umi-OCR/releases/latest">
    <img src="https://img.shields.io/github/v/release/qwedc001/tesseractOCR_umi_plugin?style=flat-square" alt="Umi-OCR">
  </a>
  <a href="License">
    <img src="https://img.shields.io/github/license/qwedc001/tesseractOCR_umi_plugin?style=flat-square" alt="LICENSE">
  </a>
</p>

## 开始使用

### 对于用户

下载 release 中已经打包好的插件，放入 Umi-OCR 的 plugins 文件夹中即可使用。

### 对于开发者

如果您想对本插件进行二次开发，可以通过以下步骤进行安装：

1.clone 此项目到本地

2.本地建立一个独立的 python 3.8.10 x64 虚拟环境。

3.执行

```
pip install Pillow,pytesseract
```

4.将下载好的 Tesseract 程序文件夹重命名为 engine 并放在该文件夹下。

### 添加额外语言

release 包中内置有中英日以及数学识别语言库，如果您所需的语言不在其中，您可以前往 [Tesseract_Fast](https://github.com/tesseract-ocr/tessdata_fast) 或者 [Tesseract_best](https://github.com/tesseract-ocr/tessdata_best) 寻找您所需要的语言库，下载后将其放入 engine/tessdata 文件夹中即可。

## 关于 Umi-OCR 项目结构

### 各仓库：

- [主仓库](https://github.com/hiroi-sora/Umi-OCR)
- [插件库](https://github.com/hiroi-sora/Umi-OCR_plugins) -> [本插件项目](https://github.com/qwedc001/tesseractOCR_umi_plugin)👈
- [Win 运行库](https://github.com/hiroi-sora/Umi-OCR_runtime_windows)

### 工程结构：

`**` 后缀表示本仓库(`插件仓库`)包含的内容。

```
tesseractOCR_umi_plugin
├─ __init__.py **
├─ api_tesseractocr.py **
├─ i18n.csv **
├─ tesseractocr_config.py **
├─ engine
│  └─ tesseractOCR 的核心引擎文件
└─ site-packages
    └─ tesseractOCR 的依赖库
```
