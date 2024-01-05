from plugin_i18n import Translator

tr = Translator(__file__, "i18n.csv")

globalOptions = {
    "title": tr("TesseractOCR（本地）"),
    "type": "group",
}

localOptions = {
    "title": tr("TesseractOCR（本地）"),
    "type": "group",
    "short_size": {
        "title": tr("限制图像边长"),
        "optionsList": [
            [960, "960 " + tr("（默认）")],
            [2880, "2880"],
            [4320, "4320"],
            [999999, tr("无限制")],
        ],
        "toolTip": tr("将边长大于该值的图片进行压缩，可以提高识别速度。可能降低识别精度。"),
    },
}