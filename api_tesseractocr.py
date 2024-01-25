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
                print(argd['vert'])
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

    def standardize(self,res):
        # ['level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num', 'left', 'top', 'width', 'height', 'conf', 'text']
        datas = []
        for item in res[2:]: # 第一行为固定的提示表头
            text = item[11]
            score = float(item[10])
            if score == -1:
                continue
            left,top,width,height = int(item[6]), int(item[7]), int(item[8]), int(item[9])
            topLeft = [left,top]
            topRight = [left+width,top]
            bottomLeft = [left,top+height]
            bottomRight = [left+width,top+height]
            box = [topLeft,topRight, bottomRight, bottomLeft]
            # FIXIT: box目前实现存在异常，会影响box显示以及竖屏的排版
            datas.append({"text":text,"score":score,"box":box})
            print({"text":text,"score":score,"box":box})
        if datas:
            out = {"code": 100, "data": datas}
        else:
            out = {"code": 101, "data": ""}
        return out

    # 获取OcrHandle 实例
    def start(self, argd):
        self.psm = "--psm 3" if argd['psm'] else "--psm 6" # psm 3: 自动分页 psm6: 单文本块分页  magic number来源：tesseract docs
        try:
            langs = self.get_select_languages(argd)
            self.languages = "+".join(langs)
            print(self.languages)
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
