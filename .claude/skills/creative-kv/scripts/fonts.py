"""フォント解決（Windows前提。無ければ順に代替）。HG系フォントはOffice同梱なので別PCでは無いことがある。"""
from PIL import ImageFont
import os
F = os.environ.get("WINDIR", "C:/Windows") + "/Fonts/"
CHAINS = {
    "mincho_heavy": ["HGRME.TTC", "yumindb.ttf", "NotoSerifJP-VF.ttf", "BIZ-UDMinchoM.ttc", "msmincho.ttc"],
    "mincho_bold":  ["HGRMB.TTC", "yumindb.ttf", "NotoSerifJP-VF.ttf", "BIZ-UDMinchoM.ttc", "msmincho.ttc"],
    "serif_en":      ["BOOKOS.TTF", "CENTURY.TTF", "georgia.ttf", "times.ttf"],
    "serif_en_bold": ["BOOKOSB.TTF", "CENTURY.TTF", "georgiab.ttf", "timesbd.ttf"],
    "pop":       ["HGRPRE.TTC", "HGRPP1.TTC", "UDDigiKyokashoN-B.ttc", "YuGothB.ttc"],
    "kyokasho":  ["UDDigiKyokashoN-B.ttc", "HGRKK.TTC", "YuGothM.ttc"],
}

def font(kind, size):
    for name in CHAINS[kind]:
        p = F + name
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()
