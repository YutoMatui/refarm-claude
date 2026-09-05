# -*- coding: utf-8 -*-
"""API課金の共有台帳。だれが・いつ・何に・いくら使ったかを1か所に貯める。

メンバーがそれぞれのパソコンで生成すると、記録がバラバラになって誰も全体を把握できない。
そこで台帳は Google Drive に置く（＝全員が同じファイルに追記する）。

    python cost.py              … 今月のレポート（だれがいくら）
    python cost.py 全部          … 月ごとの合計もぜんぶ
    python cost.py 上限 5000     … 月の上限を変える（全員に効く）

【重要】この台帳に載るのは、このスキルのスクリプトを通した分だけ。
本当の請求額は Google Cloud Console → お支払い → レポート が正。
月末はかならずそちらと突き合わせること。
"""
import json
import os
import socket
import sys
import time

DRIVE = r"G:\マイドライブ\50日企画素材"
LOCAL = os.path.dirname(os.path.abspath(__file__))
JPY_PER_USD = 150

# 単価（2026-09時点。変わったらここを直す）
PRICES = {
    "veo-3.1-fast": ("動画", 0.15, "1秒あたり"),
    "gemini-3-pro-image": ("画像", 0.134, "1枚あたり(1K/2K)"),
    "gemini-3-pro-image-4k": ("画像", 0.24, "1枚あたり(4K)"),
    "gemini-2.5-flash-image": ("画像", 0.039, "1枚あたり"),
}


def ledger_path():
    """台帳の場所。Driveが見えていればDrive、見えなければ手元に貯めておく。"""
    if os.path.isdir(DRIVE):
        return os.path.join(DRIVE, "_API利用ログ.jsonl"), True
    return os.path.join(LOCAL, "_API利用ログ_ローカル.jsonl"), False


def config_path():
    if os.path.isdir(DRIVE):
        return os.path.join(DRIVE, "_API利用ログ_設定.json")
    return os.path.join(LOCAL, "_API利用ログ_設定.json")


def monthly_cap():
    p = config_path()
    if os.path.exists(p):
        try:
            return int(json.load(open(p, encoding="utf-8")).get("monthly_cap_jpy", 3000))
        except Exception:
            pass
    return 3000


def set_cap(v):
    json.dump({"monthly_cap_jpy": int(v)}, open(config_path(), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("月の上限を %d円 にしました（全員に効きます）" % int(v))


def who():
    return "%s@%s" % (os.environ.get("USERNAME", "?"), socket.gethostname())


def api_key():
    """APIキーは環境変数から読む。スクリプトにも設定ファイルにも書かない。

    このリポジトリの他のツール（tools/generate_image.py）に合わせて GEMINI_API_KEY を先に見る。
    """
    k = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not k:
        print("エラー: APIキーが設定されていません。")
        print("  PowerShellで一度だけ:  setx GEMINI_API_KEY \"（もらったキー）\"")
        print("  そのあとターミナルを開き直してください。")
        sys.exit(1)
    return k


def estimate(model, qty):
    """qty = 動画なら秒数、画像なら枚数。"""
    if model not in PRICES:
        return 0, 0.0
    usd = PRICES[model][1] * qty
    return round(usd * JPY_PER_USD), usd


def record(model, qty, detail, ok=True):
    """1回ぶんを台帳に書く。失敗ぶんも書く（サーバー側では生成済み＝課金されるため）。"""
    jpy, usd = estimate(model, qty)
    line = {"at": time.strftime("%Y-%m-%d %H:%M"), "who": who(), "model": model,
            "qty": qty, "detail": detail, "usd": round(usd, 3), "jpy": jpy, "ok": ok}
    p, on_drive = ledger_path()
    # 1行1件の追記なので、複数のパソコンから同時に書いても壊れない
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")
    if not on_drive:
        print("  ※ Driveが見えないので手元に記録しました。あとで共有台帳に載りません。")
    return jpy


def read_all():
    p, _ = ledger_path()
    rows = []
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                try:
                    rows.append(json.loads(ln))
                except Exception:
                    pass
    # Driveに移る前の手元ぶんも足す
    lp = os.path.join(LOCAL, "_API利用ログ_ローカル.jsonl")
    if os.path.exists(lp) and lp != p:
        for ln in open(lp, encoding="utf-8"):
            if ln.strip():
                try:
                    rows.append(json.loads(ln))
                except Exception:
                    pass
    return rows


def month_total(ym=None):
    ym = ym or time.strftime("%Y-%m")
    return sum(r["jpy"] for r in read_all() if r["at"].startswith(ym))


def check_budget(model, qty):
    """使う前に呼ぶ。上限を超えるなら False と理由を返す。"""
    jpy, _ = estimate(model, qty)
    used, cap = month_total(), monthly_cap()
    if used + jpy > cap:
        return False, jpy, used, cap
    return True, jpy, used, cap


def report(everything=False):
    rows = read_all()
    p, on_drive = ledger_path()
    if not on_drive:
        print("※ Google Drive が見えていません。手元のぶんだけ出しています。")
    if not rows:
        print("まだ1件も記録がありません。")
        return

    ym = time.strftime("%Y-%m")
    cur = [r for r in rows if r["at"].startswith(ym)]
    cap = monthly_cap()
    total = sum(r["jpy"] for r in cur)

    print("=== %s の利用状況 ===" % ym)
    print("合計 %d円 / 上限 %d円  (%d%%)" % (total, cap, round(total / cap * 100) if cap else 0))
    print("")

    if cur:
        print("[だれが]")
        by_who = {}
        for r in cur:
            by_who.setdefault(r["who"], [0, 0])
            by_who[r["who"]][0] += r["jpy"]
            by_who[r["who"]][1] += 1
        for k, (jpy, n) in sorted(by_who.items(), key=lambda x: -x[1][0]):
            print("  %-28s %6d円  (%d回)" % (k, jpy, n))

        print("")
        print("[何に]")
        by_model = {}
        for r in cur:
            by_model.setdefault(r["model"], [0, 0])
            by_model[r["model"]][0] += r["jpy"]
            by_model[r["model"]][1] += 1
        for k, (jpy, n) in sorted(by_model.items(), key=lambda x: -x[1][0]):
            label = PRICES.get(k, ("?",))[0]
            print("  %-24s %-4s %6d円  (%d回)" % (k, label, jpy, n))

        ng = [r for r in cur if not r["ok"]]
        if ng:
            print("")
            print("  うち失敗ぶん %d円 (%d回) ※失敗しても課金されます" %
                  (sum(r["jpy"] for r in ng), len(ng)))

        print("")
        print("[直近]")
        for r in cur[-10:]:
            print("  %s %-20s %-22s %5d円 %s" %
                  (r["at"], r["who"][:20], r["detail"][:22], r["jpy"],
                   "" if r["ok"] else "(失敗)"))

    if everything:
        print("")
        print("[月ごと]")
        by_m = {}
        for r in rows:
            by_m[r["at"][:7]] = by_m.get(r["at"][:7], 0) + r["jpy"]
        for k in sorted(by_m):
            print("  %s  %6d円" % (k, by_m[k]))

    print("")
    print("台帳: %s" % p)
    print("※ ここに出るのはスクリプト経由の分だけです。")
    print("  本当の請求は Google Cloud Console → お支払い → レポート で確認してください。")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] in ("上限", "cap"):
        if len(a) < 2:
            print("今の上限: %d円" % monthly_cap())
        else:
            set_cap(a[1])
    elif a and a[0] in ("全部", "all"):
        report(True)
    else:
        report()
