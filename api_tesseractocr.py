import os
import sys
import site
import base64
from PIL import Image
from io import BytesIO

# 当前目录
CurrentDir = os.path.dirname(os.path.abspath(__file__))
# 依赖包目录
SitePackages = os.path.join(CurrentDir, "site-packages")

class Api:
    def __init__(self, globalArgd):
        self.tesseractOcr = None

    # 获取OcrHandle 实例
    def start(self, argd):
        self.short_size = argd["short_size"]  # 记录最新 short_size 参数
        self.config = {

        }
        if self.tesseractOcr:  # 引擎已启动，则跳过再启动
            return ""
        site.addsitedir(SitePackages)  # 依赖库到添加python搜索路径
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = r'./engine/tesseract.exe'
            self.tesseractOcr=pytesseract
            return ""
        except Exception as e:
            self.tesseractOcr = None
            err = str(e)
            print(err)
            return f"[Error] Error on loading:{err}"

    def stop(self):
        self.tesseractOcr = None

    # 借用自plugins-P2Tocr,进行了修改
    def _standardized(self, res):
        datas = []
        for item in res:
            text = item[1]
            accuracy = item[2]
            position = item[0]
            datas.append(
                {
                    "text": text,
                    "score": accuracy,
                    "box": position,
                }
            )
        if datas:
            out = {"code": 100, "data": datas}
        else:
            out = {"code": 101, "data": ""}
        return out

    def _run(self, img: Image):
        if not self.tesseractOcr:
            res = {"code": 201, "data": "tesseractOcr not initialized."}
        else:
            try:
                res = self.tesseractOcr.image_to_data(img,**self.config)
                res = self.mergeData(res)
                res = self._standardized(res)
            except Exception as e:
                return {"code": 202, "data": f"tesseractOcr recognize error:{e}"}
        return res

    def runPath(self, imgPath: str):
        return self._run(imgPath)

    def runBytes(self, imgBytes: bytes):
        return self._run(Image.open(BytesIO(imgBytes)))

    def runBase64(self, imgBase64: str):
        return self._run(Image.open(BytesIO(base64.b64decode(imgBase64))))
