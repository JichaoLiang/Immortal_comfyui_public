import os.path
import sys
# from . import Utils
# import Utils

class ImmortalConfig:
    base = r"d:\immortaldata"
    basepath = os.path.join(base, "Immortal")
    sucaipath = os.path.join(basepath, r"sucai")
    packpath = os.path.join(basepath, r'package')
    bgmpath = os.path.join(basepath, r'bgm')
    objectStorePath = os.path.join(basepath, "objectstore")
    cosyvoiceurl = "http://localhost:9880"

    font_douyin = r"C:\Windows\Fonts\douyinmeihaoti.otf"
    font_fanti1 = "C:\\Users\\Administrator\\AppData\\Local\\Microsoft\\Windows\\Fonts\\hanyialitifan.ttf"
    font_douyu = r"C:\Users\Administrator\AppData\Local\Microsoft\Windows\Fonts\douyuzhuiguangti.ttf"
    font_simhei = r"C:\Windows\Fonts\simhei.ttf"
    lstmsynchost = r"http://127.0.0.1:8787/"

    subtitlefont = font_simhei

    imagewhitelist = ["jpg", "png"]
    videowhitelist = ["mp4"]
    audiowhitelist = ["mp3", "wav"]

    @staticmethod
    def grepFullpath(id, basedir):
        grepsubdirlist = ["images", "videos", "audios"]
        availablelist = ImmortalConfig.imagewhitelist + ImmortalConfig.videowhitelist + ImmortalConfig.audiowhitelist
        for subd in grepsubdirlist:
            for avn in availablelist:
                targetpath = os.path.join(basedir, subd, f"{id}.{avn}")
                if os.path.exists(targetpath):
                    return targetpath
        return None;
        pass

    pass