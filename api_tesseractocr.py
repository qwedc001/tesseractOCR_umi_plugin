import os
import site
import base64
from PIL import Image
from io import BytesIO
import traceback
import unicodedata

# 当前目录
CurrentDir = os.path.dirname(os.path.abspath(__file__))
# 依赖包目录
SitePackages = os.path.join(CurrentDir, "site-packages")

ModelDir = os.path.join(CurrentDir, "engine/tessdata/")


class Api:
    def __init__(self, globalArgd):
        self.tesseractOcr = None
        self.accuracy = float(globalArgd["accur"])

    def get_select_languages(self, argd) -> list:
        selects = []
        for k, flag in argd.items():
            if k.startswith("language.") and flag:
                language = k[9:]
                if (language == "chi_sim" or language == "chi_tra") and argd["vert"]:
                    selects.append(language + "_vert")
                selects.append(language)
        return selects

    @staticmethod  # 按 key 取一行的内容
    def _get_r(row, key):
        tessKey = {  # TesseratOCR 结果表格下标与键的映射
            "level": 0,
            "page_num": 1,
            "block_num": 2,
            "par_num": 3,
            "line_num": 4,
            "word_num": 5,
            "left": 6,
            "top": 7,
            "width": 8,
            "height": 9,
            "conf": 10,
            "text": 11,
        }
        if key == "text":
            return str(row[tessKey[key]])
        elif key == "conf":
            return float(row[tessKey[key]])
        else:
            return int(row[tessKey[key]])

    @staticmethod  # 传入前句尾字符和后句首字符，返回分隔符
    def _word_separator(letter1, letter2):

        # 判断Unicode字符是否属于中文、日文或韩文字符集
        def is_cjk(character):
            cjk_unicode_ranges = [
                (0x4E00, 0x9FFF),  # 中文
                (0x3040, 0x30FF),  # 日文
                (0x1100, 0x11FF),  # 韩文
                (0x3130, 0x318F),  # 韩文兼容字母
                (0xAC00, 0xD7AF),  # 韩文音节
                # 全角符号
                (0x3000, 0x303F),  # 中文符号和标点
                (0xFE30, 0xFE4F),  # 中文兼容形式标点
                (0xFF00, 0xFFEF),  # 半角和全角形式字符
            ]
            return any(
                start <= ord(character) <= end for start, end in cjk_unicode_ranges
            )

        if is_cjk(letter1) and is_cjk(letter2):
            return ""

        # 特殊情况：前文为连字符。
        if letter1 == "-":
            return ""
        # 特殊情况：后文为任意标点符号。
        if unicodedata.category(letter2).startswith("P"):
            return ""
        # 其它正常情况加空格
        return " "

    @staticmethod  # 测试用：打印结果表格
    def _test_print_table(res):
        # ['level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num', 'left', 'top', 'width', 'height', 'conf', 'text']
        print("原始输出：\n")
        # 计算每列的最大宽度
        col_widths = [max(len(str(item)) for item in col) for col in zip(*res)]
        for row in res:
            s = " ".join(str(item).ljust(col_widths[i]) for i, item in enumerate(row))
            print(s)

    @staticmethod  # 测试用：打印结果字典
    def _test_print_datas(datas):
        for d in datas:
            print(f'{d["score"]:.3f}|{d["text"]}|【{repr(d["end"])}】')

    def calcBox(self, left, right):
        topLeft = left[0]
        topRight = right[1] if right else left[1]
        bottomLeft = left[3]
        bottomRight = right[2] if right else left[2]
        return [topLeft, topRight, bottomRight, bottomLeft]

    def standardize(self, res):
        # self._test_print_table(res)
        datas = []
        # 当前行的信息
        data = None
        text = ""
        score = 0
        num = 0
        last_level = -1
        # 遍历所有行
        for index in range(1, len(res)):
            row = res[index]
            level = self._get_r(row, "level")
            # 结束上一行
            if last_level == 5 and level != 5:
                if not text.isspace():  # 跳过纯空格行
                    data["text"] = text
                    data["score"] = score / (max(num, 1) * 100)
                    # 若 level 不是 line ，说明新一行不属于同一自然段，结尾要换行
                    if level != 4:
                        data["end"] = "\n"
                    datas.append(data)
            # 发现新的一行
            if level == 4:
                left = self._get_r(row, "left")
                top = self._get_r(row, "top")
                width = self._get_r(row, "width")
                height = self._get_r(row, "height")
                data = {
                    "box": [
                        [left, top],
                        [left + width, top],
                        [left + width, top + height],
                        [left, top + height],
                    ],
                }
                score = 0
                num = 0
                text = ""
            # 补充当前行
            if level == 5:
                sep = ""
                now_text = self._get_r(row, "text")
                if text and now_text:  # 获取间隔符
                    sep = self._word_separator(text[-1], now_text[0])
                text += sep + now_text
                score += self._get_r(row, "conf")
                num += 1
            last_level = level
        # 遍历所有结果，补充 ["end"] 参数
        for index in range(len(datas) - 1):
            d1 = datas[index]
            if "end" in d1:  # 跳过已有
                continue
            d2 = datas[index + 1]  # 下一行
            d1["end"] = self._word_separator(d1["text"][-1], d2["text"][0])
        # self._test_print_datas(datas)
        if datas:
            out = {"code": 100, "data": datas}
        else:
            out = {"code": 101, "data": ""}
        return out

    # 获取OcrHandle 实例
    def start(self, argd):
        self.psm = (
            "--psm 3" if argd["psm"] else "--psm 6"
        )  # psm 3: 自动分页 psm6: 单文本块分页  magic number来源：tesseract docs
        try:
            langs = self.get_select_languages(argd)
            self.languages = "+".join(langs)
            if self.tesseractOcr:  # 引擎已启动，则跳过再启动
                return ""
            site.addsitedir(SitePackages)  # 依赖库到添加python搜索路径
            import pytesseract

            pytesseract.pytesseract.tesseract_cmd = os.path.join(
                CurrentDir, "engine/tesseract.exe"
            )
            self.tesseractOcr = pytesseract
            return ""
        except Exception as e:
            self.tesseractOcr = None
            err = str(e)
            return f"[Error] Error on loading engine:{err}"

    def stop(self):
        self.tesseractOcr = None

    def _run(self, img: Image):
        if not self.tesseractOcr:
            res = {"code": 201, "data": "tesseractOcr not initialized."}
        else:
            try:
                res = [
                    item.split("\t")
                    for item in self.tesseractOcr.image_to_data(
                        img, lang=self.languages, config=self.psm
                    ).split("\n")
                ][
                    :-1
                ]  # TODO: 此处tesseract docs实际上给出的command line example很少，所以此处的config以最重要的psm先代替，其他的需要再多研究一下docs再加入
                res.append(
                    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, ""]
                )  # 确保所有的文字都被正确append
                res = self.standardize(res)
            except Exception as e:
                traceback.print_exc()
                return {"code": 202, "data": f"tesseractOcr recognize error:{e}"}
        return res

    def runPath(self, imgPath: str):
        return self._run(imgPath)

    def runBytes(self, imgBytes: bytes):
        return self._run(Image.open(BytesIO(imgBytes)))

    def runBase64(self, imgBase64: str):
        return self._run(Image.open(BytesIO(base64.b64decode(imgBase64))))
