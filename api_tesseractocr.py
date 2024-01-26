import os
import sys
import site
import base64
from PIL import Image
from io import BytesIO
import traceback

# 当前目录
CurrentDir = os.path.dirname(os.path.abspath(__file__))
# 依赖包目录
SitePackages = os.path.join(CurrentDir, "site-packages")

TESSERACT_SUPPORTED = ['afr', 'amh', 'ara', 'asm', 'aze', 'aze', 'bel', 'ben', 'bod', 'bos', 'bre', 'bul', 'cat', 'ceb', 'ces', 'chi', 'chi', 'chr', 'cos', 'cym', 'dan', 'deu', 'div', 'dzo', 'ell', 'Mod', '145', 'eng', 'enm', 'Mid', '110', 'epo', 'equ', 'est', 'eus', 'fas', 'fao', 'fil', 'fin', 'fra', 'frk', 'frm', 'Mid', 'ca.', 'fry', 'gla', 'gle', 'glg', 'grc', 'Anc', 'to ', 'guj', 'hat', 'heb', 'hin', 'hrv', 'hun', 'hye', 'iku', 'ind', 'isl', 'ita', 'ita', 'jav', 'jpn', 'kan', 'kat', 'kat', 'kaz', 'khm', 'kir', 'kmr', 'kor', 'kor', 'lao', 'lat', 'lav', 'lit', 'ltz', 'mal', 'mar', 'mkd', 'mlt', 'mon', 'mri', 'msa', 'mya', 'nep', 'nld', 'nor', 'oci', 'ori', 'osd', 'pan', 'pol', 'por', 'pus', 'que', 'ron', 'rus', 'san', 'sin', 'slk', 'slv', 'snd', 'spa', 'spa', 'sqi', 'srp', 'srp', 'sun', 'swa', 'swe', 'syr', 'tam', 'tat', 'tel', 'tgk', 'tha', 'tir', 'ton', 'tur', 'uig', 'ukr', 'urd', 'uzb', 'uzb', 'vie', 'yid', 'yor']
ModelDir = os.path.join(CurrentDir,"engine/tessdata/")

class Api:
    def __init__(self, globalArgd):
        self.tesseractOcr = None
    
    def check(self,languages:list) -> (list,list):
        unsupported = []
        uninstalled = []
        for language in languages:
            if language not in TESSERACT_SUPPORTED:
                unsupported.append(language)
            elif not os.path.exists(ModelDir + language + ".traineddata"):
                uninstalled.append(language)
        return (unsupported,uninstalled)

    def get_select_languages(self,argd) -> list:
        selects = []
        for k,flag in argd.items():
            if k == "language.~enabledOther" or k == 'language.~other':
                continue
            if k.startswith("language.") and flag:
                language = k[9:]
                if (language == 'chi_sim' or language == "chi_tra") and argd['vert']:
                        selects.append(language+"_vert")
                selects.append(language)
        if argd['language.~enabledOther']:
            otherLangs = argd['language.~other'].split(" ")
            unsupported,uninstalled = self.check(otherLangs)
            if len(unsupported):
                raise Exception(f"Unsupported languages: {unsupported}")
            if len(uninstalled):
                raise Exception(f"Uninstalled languages: {uninstalled}")
            selects += otherLangs
        return selects

    # 获取两个连续单词的分隔符。letter1为单词1结尾字母，letter2为单词2结尾字母
    def _word_separator(self, letter1, letter2):
        # 判断结尾和开头，是否属于汉藏语族
        # 汉藏语族：行间无需分割符。印欧语族：则两行之间需加空格。
        ranges = [
            (0x4E00, 0x9FFF),  # 汉字
            (0x3040, 0x30FF),  # 日文
            (0xAC00, 0xD7AF),  # 韩文
            (0xFF01, 0xFF5E),  # 全角字符
        ]
        fa, fb = False, False
        for l, r in ranges:
            if l <= ord(letter1) <= r:
                fa = True
            if l <= ord(letter2) <= r:
                fb = True
        if fa and fb: # 两个字符都是汉藏语族，才没有空格
            return ""

        # 特殊情况：字母2为缩写，如 n't。或者字母2为结尾符号，意味着OCR错误分割。
        if letter2 in {r"'", ",", ".", "!", "?", ";", ":"}:
            return ""
        # 其它正常情况，如 俩单词 或 一单词一汉字，加空格
        return " "
    
    def calcBox(self,left,right):
        topLeft = left[0]
        topRight = right[1] if right else left[1]
        bottomLeft = left[3]
        bottomRight = right[2] if right else left[2]
        return [topLeft,topRight, bottomRight, bottomLeft]

    def standardize(self,res):
        # ['level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num', 'left', 'top', 'width', 'height', 'conf', 'text']
        datas = []
        curString = ""
        curLeftBox = None
        curRightBox = None
        scores = []
        for item in res[2:]: # 第一行为固定的提示表头
            text = item[11]
            score = float(item[10])
            level = int(item[0]) # level 为 5 时为单词，依据此进行组句
            left,top,width,height = int(item[6]), int(item[7]), int(item[8]), int(item[9])
            topLeft = [left,top]
            topRight = [left+width,top]
            bottomLeft = [left,top+height]
            bottomRight = [left+width,top+height]
            box = [topLeft,topRight, bottomRight, bottomLeft]
            if level != 5 and len(scores) != 0:
                final = 0
                for i in range(len(scores)):
                    final += scores[i]
                datas.append({"text": curString, "score": final / len(scores), "box": self.calcBox(curLeftBox,curRightBox)})
                curRightBox = None
                curLeftBox = None
                scores = []
                curString = ""
                continue
            if level == 5:
                if score <= self.accuracy:
                    continue
                if curString == "": # 开头不做处理
                    curLeftBox = box
                    curString = text
                else:
                    curRightBox = box
                    curString += self._word_separator(curString[-1],text[-1])+text
                scores.append(score)
                continue
            else: # 多个非 level5 相连则不做处理，直接跳过即可
                continue
        if datas:
            out = {"code": 100, "data": datas}
        else:
            out = {"code": 101, "data": ""}
        return out

    # 获取OcrHandle 实例
    def start(self, argd):
        self.psm = "--psm 3" if argd['psm'] else "--psm 6" # psm 3: 自动分页 psm6: 单文本块分页  magic number来源：tesseract docs
        self.accuracy = float(argd['accur'])
        try:
            langs = self.get_select_languages(argd)
            self.languages = "+".join(langs)
            if self.tesseractOcr:  # 引擎已启动，则跳过再启动
                return ""
            site.addsitedir(SitePackages)  # 依赖库到添加python搜索路径
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = os.path.join(CurrentDir,'engine/tesseract.exe')
            self.tesseractOcr=pytesseract
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
                res = [item.split('\t') for item in self.tesseractOcr.image_to_data(img, lang=self.languages,config=self.psm).split('\n')][:-1] # TODO: 此处tesseract docs实际上给出的command line example很少，所以此处的config以最重要的psm先代替，其他的需要再多研究一下docs再加入
                res.append([-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,""]) # 确保所有的文字都被正确append
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
