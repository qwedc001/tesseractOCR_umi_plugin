<h1 align="center">适用于 Umi-OCR 文字识别工具 的 TesseractOCR 插件</h1>

<p align="center">
  <a href="https://github.com/qwedc001/tesseractOCR_umi_plugin/releases/latest">
    <img src="https://img.shields.io/github/v/release/qwedc001/tesseractOCR_umi_plugin?style=flat-square" alt="Umi-OCR">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/github/license/qwedc001/tesseractOCR_umi_plugin?style=flat-square" alt="LICENSE">
  </a>
</p>

## 插件说明

将本插件加载进 [Umi-OCR](https://github.com/hiroi-sora/Umi-OCR) 即可使用。

与其他插件（如PaddleOCR）相比， TesseractOCR 有这些 **优点** ：

- 👍 英文语言的识别准确率高，且不易出现空格丢失现象。
- 👍 自带段落分析模型，对书籍/论文排版具有精度非常好的识别率。
- 👍 允许同时勾选多个语言库（如中文+英文+日文）进行识别。
- 👍 使用 fast 模型库时，识别速度比 Paddle 更快。

TesseractOCR 有这些 **缺点** ：

- 🙁 汉字体系的语言（如中文、日文），准确率欠佳。

TesseractOCR 的 **适用场景** ：

- 纯英文内容。
- 需要解析文章排版，如PDF识别时。

## 开始使用

### 对于用户

1. 下载 release 中已经打包好的插件，放入 `Umi-OCR/UmiOCR-data/plugins` 文件夹中。
2. 启动 Umi-OCR ，将 **全局设置** → **文字识别** → **当前接口** 改为 `TesseractOCR` ，然后 **点击** `应用修改` 。
3. 在各个标签页（如`批量OCR`）中，将 **设置** → **排版解析方案** 改为 `不做处理` ，以便启用TesseractOCR自带的排版解析模型。

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

release 包中内置有中英日以及数学识别语言库，如果您所需的语言不在其中，您可以前往 [Tesseract_Fast](https://github.com/tesseract-ocr/tessdata_fast) 或者 [Tesseract_best](https://github.com/tesseract-ocr/tessdata_best) 寻找您所需要的语言库`**.traineddata`，下载后将其放入 engine/tessdata 文件夹中即可。

### 工程结构：

`**` 后缀表示本仓库(`插件仓库`)包含的代码文件。

其他文件请在Release包中获取。

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
