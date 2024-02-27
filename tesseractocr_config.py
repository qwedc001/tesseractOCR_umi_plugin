from plugin_i18n import Translator
import os

tr = Translator(__file__, "i18n.csv")

TESSERACT_SUPPORTED = {
    "afr": "Afrikaans",
    "amh": "Amharic",
    "ara": "Arabic",
    "asm": "Assamese",
    "aze": "Azerbaijani",
    "aze_cyrl": "Azerbaijani - Cyrilic",
    "bel": "Belarusian",
    "ben": "Bengali",
    "bod": "Tibetan",
    "bos": "Bosnian",
    "bre": "Breton",
    "bul": "Bulgarian",
    "cat": "Catalan; Valencian",
    "ceb": "Cebuano",
    "ces": "Czech",
    "chi_sim": "简体中文",
    "chi_tra": "繁體中文",
    "chr": "Cherokee",
    "cos": "Corsican",
    "cym": "Welsh",
    "dan": "Danish",
    "deu": "German",
    "div": "Dhivehi",
    "dzo": "Dzongkha",
    "ell": "Greek, Modern, 1453-",
    "eng": "English",
    "enm": "English, Middle, 1100-1500",
    "epo": "Esperanto",
    "equ": tr("数学公式"),
    "est": "Estonian",
    "eus": "Basque",
    "fas": "Persian",
    "fao": "Faroese",
    "fil": "Filipino",
    "fin": "Finnish",
    "fra": "French",
    "frk": "Frankish",
    "frm": "French, Middle, ca.1400-1600",
    "fry": "West Frisian",
    "gla": "Scottish Gaelic",
    "gle": "Irish",
    "glg": "Galician",
    "grc": "Greek, Ancient, to 1453",
    "guj": "Gujarati",
    "hat": "Haitian; Haitian Creole",
    "heb": "Hebrew",
    "hin": "Hindi",
    "hrv": "Croatian",
    "hun": "Hungarian",
    "hye": "Armenian",
    "iku": "Inuktitut",
    "ind": "Indonesian",
    "isl": "Icelandic",
    "ita": "Italian",
    "ita_old": "Italian - Old",
    "jpn": "日本語",
    "jav": "Javanese",
    "kan": "Kannada",
    "kat": "Georgian",
    "kat_old": "Georgian - Old",
    "kaz": "Kazakh",
    "khm": "Central Khmer",
    "kir": "Kirghiz; Kyrgyz",
    "kmr": "Kurdish Kurmanji",
    "kor": "한국어",
    "kor_vert": "Korean vertical",
    "lao": "Lao",
    "lat": "Latin",
    "lav": "Latvian",
    "lit": "Lithuanian",
    "ltz": "Luxembourgish",
    "mal": "Malayalam",
    "mar": "Marathi",
    "mkd": "Macedonian",
    "mlt": "Maltese",
    "mon": "Mongolian",
    "mri": "Maori",
    "msa": "Malay",
    "mya": "Burmese",
    "nep": "Nepali",
    "nld": "Dutch; Flemish",
    "nor": "Norwegian",
    "oci": "Occitan post 1500",
    "ori": "Oriya",
    "pan": "Panjabi; Punjabi",
    "pol": "Polish",
    "por": "Portuguese",
    "pus": "Pushto; Pashto",
    "que": "Quechua",
    "ron": "Romanian; Moldavian; Moldovan",
    "rus": "Русский",
    "san": "Sanskrit",
    "sin": "Sinhala; Sinhalese",
    "slk": "Slovak",
    "slv": "Slovenian",
    "snd": "Sindhi",
    "spa": "Spanish; Castilian",
    "spa_old": "Spanish; Castilian - Old",
    "sqi": "Albanian",
    "srp": "Serbian",
    "srp_latn": "Serbian - Latin",
    "sun": "Sundanese",
    "swa": "Swahili",
    "swe": "Swedish",
    "syr": "Syriac",
    "tam": "Tamil",
    "tat": "Tatar",
    "tel": "Telugu",
    "tgk": "Tajik",
    "tha": "Thai",
    "tir": "Tigrinya",
    "ton": "Tonga",
    "tur": "Turkish",
    "uig": "Uighur; Uyghur",
    "ukr": "Ukrainian",
    "urd": "Urdu",
    "uzb": "Uzbek",
    "uzb_cyrl": "Uzbek - Cyrilic vie Vietnamese",
    "yid": "Yiddish",
    "yor": "Yoruba",
}


def _dymanicLangList():
    modelsPath = os.path.dirname(os.path.abspath(__file__)) + "/engine/tessdata"
    files = os.listdir(modelsPath)
    defaultModel = None
    if "eng.traineddata" in files:
        defaultModel = "eng"
    for fileName in files:
        if fileName.endswith(".traineddata") and not fileName.endswith(
            "vert.traineddata"
        ):
            modelName = fileName.split(".")[0]
            if (
                not modelName in localOptions["language"]
                and modelName in TESSERACT_SUPPORTED
            ):
                localOptions["language"][modelName] = {
                    "title": TESSERACT_SUPPORTED[modelName],
                    "default": False,
                }
                if not defaultModel:
                    defaultModel = modelName
    if not defaultModel:
        raise Exception("TesseractOCR 插件未能在模型目录中找到任何语言的识别模型")
    localOptions["language"][defaultModel]["default"] = True


globalOptions = {
    "title": tr("TesseractOCR（本地）"),
    "type": "group",
    "accur": {
        "title": tr("置信度下限"),
        "toolTip": tr("识别数据中低于该置信度的内容将会被丢弃(输入范围:0~100)"),
        "default": "60",
    },
}

localOptions = {
    "title": tr("TesseractOCR（本地）"),
    "type": "group",
    "language": {
        "title": tr("语言"),
        "type": "group",
        "toolTip": tr(
            "请在仅当文本内容包含多语言时再勾选额外识别语言，否则可能会出现识别精度下降问题。"
        ),
        "enabledFold": True,  # 启用折叠
        "fold": False,  # 默认非折叠状态。（折叠状态会保存）
    },
    "psm": {
        "title": tr("自动识别排版"),
        "toolTip": tr(
            "除非图像中只有一句文本，否则应保持开启。\n同时，建议将[排版解析方案]设为“不做处理”。"
        ),
        "default": True,
    },
    "vert": {
        "title": tr("开启竖版识别"),
        "default": False,
    },
}

_dymanicLangList()
