# -*- coding: utf-8 -*-
"""第3版の plan_v3.json を書き出す（文字を直すときはここの表を直して python make_plan_v3.py → make_draft.py plan_v3.json）

様式は pop（企業フォント・白字黒縁）。色は白だけ。OP/EDは付けない。
文字は1行を短く・大きく。縦の位置は人の顔や器にかからないところ（下から4分の1には置かない）。
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))


def size(text, top=14.0):
    """1行が画面の横幅（約960px）に収まる大きさ。数字・英字は半分の幅で数える"""
    n = sum(0.55 if ord(c) < 128 else 1 for c in text)
    return min(top, int(960 / (n * 7.7) * 2) / 2)


def card(at, lines, y, until=None, sizes=None):
    """lines を上から順に並べる（行ごとに大きさを変えるので1行ずつカードにする）"""
    out, yy = [], y
    sizes = sizes or [size(l) for l in lines]
    for i, (l, s) in enumerate(zip(lines, sizes)):
        if i:
            yy += 130 * (sizes[i - 1] + s) / 26 + 12   # 前の行と今の行の高さの半分ずつ＋すき間
        c = {"at": at, "lines": [l], "y": round(yy), "size": s}
        if until is not None:
            c["until"] = until
        out.append(c)
    return out


SEGS = [
    ("01_bow.mp4",     card(0.0, ["三宮のスープ屋さん VEGEONE は", "11月26日で", "閉店します"], 1080, sizes=[7.5, 14, 14])),
    ("02_open.mp4",    card(0.0, ["8月20日にオープンして"], 1200)),
    ("03_soups.mp4",   card(0.0, ["あっという間の3か月"], 1200)),
    ("04_thanks.mp4",  card(0.0, ["たくさんのご来店"], 1150) + card(0.6, ["ありがとうございました"], 1300)),
    ("05_work.mp4",    card(0.0, ["みなさんのおかげで"], 1200, until=1.95)
                       + card(2.0, ["毎日たのしく", "営業できました"], 1150)),
    ("06_but.mp4",     card(0.0, ["でも"], 1080, sizes=[11]) + card(0.4, ["これで終わりでは", "ありません"], 1220)),
    ("07_next.mp4",    card(0.0, ["これからは神戸市の", "マルシェやイベントで", "スープを届けます"], 1090)),
    ("08_insta.mp4",   card(0.0, ["出店の情報は", "インスタで"], 260)),
    ("09_days.mp4",    card(0.0, ["お店で食べられるのは", "あと4日だけ"], 330, until=1.9)
                       + card(1.9, ["11月の木曜", "5日・12日・19日・26日", "11:00〜14:00"], 380)),
    ("10_end.mp4",     card(0.0, ["最後に"], 330, sizes=[11]) + card(0.3, ["食べにきてください！"], 480)
                       + card(1.0, ["@refarm_soup"], 640, sizes=[9])),
]

plan = {"name": "11月閉店動画_v3", "style": "pop", "no_op_ed": True, "mute_clips": True,
        "drive_clips": "G:/マイドライブ/50日企画素材/完成動画/11月閉店動画_背景動画v3（文字なし）",
        "sources": ["clips_v3"],
        "segments": [{"clips": [{"file": f}], "telop": t} for f, t in SEGS]}
json.dump(plan, open(os.path.join(HERE, "plan_v3.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for f, t in SEGS:
    print(f, [(c["lines"][0], c["size"], c["y"]) for c in t])
