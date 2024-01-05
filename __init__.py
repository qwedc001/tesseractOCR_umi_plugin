from . import api_tesseractocr
from . import tesseractocr_config

# 插件信息
PluginInfo = {
    # 插件组别
    "group": "ocr",
    # 全局配置
    "global_options": tesseractocr_config.globalOptions,
    # 局部配置
    "local_options": tesseractocr_config.localOptions,
    # 接口类
    "api_class": api_tesseractocr.Api,
}
