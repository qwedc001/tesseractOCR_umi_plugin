from plugin_i18n import Translator

tr = Translator(__file__, "i18n.csv")

globalOptions = {
    "title": tr("TesseractOCR（本地）"),
    "type": "group",
}

localOptions = {
    "title": tr("TesseractOCR（本地）"),
    "type": "group",
    "language": {
        "title": "语言",
        "type": "group",
        "toolTip": "请在仅当文本内容包含多语言时再勾选额外识别语言，否则可能会出现识别精度下降问题。", # FIXIT: 目前该tooltip是失效状态。
        "enabledFold": True,  # 启用折叠
        "fold": False,  # 默认非折叠状态。（折叠状态会保存）
        "chi_sim": {
            "title": "中文（简体）",
            "default": True,
        },
        "chi_tra": {
            "title": "中文（繁体）",
            "default": False,
        },
        "eng": {
            "title": "English",
            "default": False,
        },
        "jpn": {
            "title": "日文",
            "default": False,
        },
        "~enabledOther": {
            "title": "启用自定义语言短码",
            "default": False,
        },
        "~other": {
            "title": "自定义语言短码",
            "toolTip":  "请查看tesseract官方文档，使用空格对所选语言进行分割。",
            "default": "",
        },
    },
    "psm":{
        "title": "自动识别排版",
        "toolTip": "设置分段格式为自动识别多块文本块排版格式，否则采用单文本块格式识别",
        "default": True,
    },
    "vert":{
        "title": "开启竖版识别",
        "toolTip": "仅限中文",
        "default": True,
    },
    "accur":{
        "title": "置信度下限",
        "toolTip": "识别数据中低于该置信度的内容将会被丢弃(输入范围:0~100)",
        "default": "60",
    }
}