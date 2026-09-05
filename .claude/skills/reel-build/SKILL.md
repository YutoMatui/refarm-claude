---
name: reel-build
description: 50日企画などのリール動画（縦1080x1920）を、Driveの撮影素材＋録音済みナレーションからffmpegで自動組み立てする手順。素材の場所・命名規則・ナレーション主導のセグメント方式・縦変換（crop方式/ぼかし背景方式）・画面録画のサービス名ぼかし・マスタリング（loudnorm+フェード）・フレーム検品までの標準工程。CapCut手作業の代わりに「完成版」品質で書き出すときに使う。
---

# リール動画組み立て（ナレーション主導・ffmpeg）

音声（ナレーション）を時間軸の主とし、映像素材を音声の尺に合わせて割り付ける方式。
テロップは付けない（CapCut等で後付け可能な状態で納品する）。

## 素材の場所（Google Drive = G:ドライブにマウント済み）

```
G:\マイドライブ\50日企画素材\
├── 間借り\                  … ECG関連の撮影素材（56本・リネーム済み）
├── 音声素材\<企画名>\        … 台本1行=1ファイルのナレーション録音（.m4a）
├── 7 14 素材\               … オープニング.mp4/エンディング.mp4（1080x1920完成素材）ほか
├── 三宮素材\・6 12 汎用素材\ … 街歩き・汎用カット
└── 完成動画\                … 納品先（このスキルの出力を置く）
```

- **命名規則**: 説明的でないファイル名（IMG_XXXX.MOV）は内容確認のうえ `IMG_XXXX_内容.MOV` にリネームしてから使う（例: `IMG_1497_PC頬杖考える.MOV`）。
- 素材はまずscratchpadにコピーしてから加工する（Drive直接読みは遅い・ロックの恐れ）。

## 組み立て方式（build_final.py の型）

実績スクリプト: `.claude/skills/reel-build/scripts/build_final.py`（間借り編2で使用）。新企画ではSEGS定義だけ差し替える。

1. **セグメント定義**: `SEGS = [(音声.m4a, [(クリップ, 開始オフセット秒), ...]), ...]`
   - 1セグメント = ナレーション1本。クリップは2〜3本まで（1本4〜5秒が目安）。
2. **尺合わせ**: 音声尺をクリップ数で均等割り→素材が足りなければ次のクリップへ回し、最後は `tpad=stop_mode=clone` で静止延長。
3. **縦変換（2方式を使い分け）**
   - 実写素材: `scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,format=yuv420p`（cropで切れてOK）
   - **画面録画・切れてはいけない素材**: 背景=拡大ぼかし＋前景=等倍フィットの重ね合わせ。
     ```
     [i:v]fps=30,setsar=1,split=2[a][b];
     [a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30,eq=brightness=-0.08[bg];
     [b]scale=-2:1920[fg];
     [bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p[v]
     ```
4. **セグメント書き出し**: libx264 / preset slow / crf 18 / aac 192k、`-t 音声尺 -shortest`。
5. **結合**: concat demuxer（`-c copy`）で `_joined.mp4`。
6. **マスタリング（最終1パス再エンコード）**:
   - 映像: `fade=t=in:st=0:d=0.5,fade=t=out:st=<全長-0.7>:d=0.7`
   - 音声: `loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.3,afade=t=out:st=<全長-0.7>:d=0.7`
   - 目標: 統合ラウドネス -16 LUFS前後（ebur128で実測確認）。

## 画面録画のサービス名ぼかし（台本ルール「サービス名は伏せる」）

- URLバーだけでなく**ページ内のロゴ・サイト内サスティッキーヘッダー**も対象。スクロールでURLバーが伸縮するとヘッダー位置が上下する点に注意。
- 手順: 録画を0.5秒刻みでフレーム抽出→ロゴが常に上部に収まる**使用区間を選ぶ**（ロゴ大写しのランディング部分は使わない）→前景スケール後に上部帯をぼかす:
  `split→crop=iw:450:0:0,gblur=sigma=28→overlay=0:0`（帯の高さは実フレームで検証して決める）。

## 落とし穴（実際に踏んだもの）

- **SAR不一致でconcatが失敗**: scaleはSARを1:1でなくす。ぼかし背景チェーンの最終overlay後に必ず `setsar=1` を入れる（エラー例: `Input link ... SAR 46079:46080 do not match ... 1:1`）。
- **Windowsのcp932問題**: subprocessは必ず `encoding="utf-8", errors="replace"` 付きで実行（ffmpegのstderrでUnicodeDecodeErrorになる）。
- コンタクトシートは ffmpeg の select+tile より「`-ss`で個別抽出→PILでタイル」が確実。

## CapCutドラフト書き出し（編集可能な形で渡す）

mp4完成品だけだとユーザーがクリップ単位の調整をできない。**同じタイムラインをCapCutドラフトとしても書き出す**（実績: `.claude/skills/reel-build/scripts/capcut_export.py`）。

- ライブラリ: `pip install pyJianYingDraft`（CapCutデスクトップのdraft_content.jsonは平文JSON。2026-07時点 CapCut 159.0.0 / draft version 360000 で動作確認済み）
- ドラフト置き場: `C:\Users\YutoM\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\`
- 素材はCapCutが参照し続けるので**安定パスにコピーしてから参照**: `C:\Users\YutoM\Videos\リール素材\<企画名>\`（scratchpadは不可＝セッション後に消える）
- 手順: `DraftFolder(...).create_draft(名前, 1080, 1920, fps=30, allow_replace=True)` → 映像/音声トラックを `append_track(TrackSpec(...))` → SEGSと同じ割り付けで `VideoSegment`/`AudioSegment` を配置 → `save()`
- **注意点（実際に踏んだもの）**:
  - 配置は全て**µs整数**で計算し「前クリップの終了=次の開始」を厳密に保証（floatの丸めでSegmentOverlap例外になる）
  - 音声素材の尺は ffprobe でなく `AudioMaterial(path).duration` を正とする（ms精度差で「素材時長超過」例外になる）
  - 映像セグメントは `volume=0.0` で現場音をミュート（ナレーションと混ざる）
  - ffmpegのフィルタ加工（ぼかし合成等）はドラフトに持ち込めない→**加工済みクリップを事前レンダリング**して1素材として渡す
  - tpadの静止延長も持ち込めない→素材尺が足りない分は警告を出し、CapCut上でフリーズ/伸長してもらう
  - CapCut起動中に生成した場合は**再起動後に一覧に出る**
  - **パスは必ず `C:/...` スラッシュ区切り**。バックスラッシュだと「異常なパス」エラーで開けない。save()後に draft_content.json / draft_meta_info.json の全パスを正規化する後処理が必須（capcut_export.py の normalize_paths）
  - **「異常なパス」の最大の原因はプラットフォーム刻印**: pyJianYingDraftは剪映（中国版）形式（platform.app_source="lv"・app_version 5.9.0・new_version 110.0.0）で書くため、CapCut国際版（"cc"・159.0.0）が拒否する。対策=CapCut自身が作った既存ドラフト（0111等）のdraft_content.jsonを骨格に、tracks/materials/duration/canvas/fpsだけ差し込む「ネイティブ化」処理（capcut_export.py 5.5節）が必須
  - allow_replace=True での再生成時、draft_meta_info.json の draft_name / draft_root_path / draft_fold_path が**空で書かれる**ことがある→後処理で明示的に設定する

## テロップ・効果音（v2以降の標準）

実績: `scripts/build_v2.py`（焼き込み版）+ `scripts/capcut_export_v2.py`（編集可能版）。

- **テロップ様式（1本目の動画に準拠）**: 白字（強調行は黄 #FFD633）・黒縁borderw=10・中央揃え・ブロック中心y=1400（下1/3）・fontsize=80・行送り102。フォントは手持ち最近似の**HG創英角ポップ体**（C:/Windows/Fonts/HGRPP1.TTC）。CapCutドラフト側はデフォルトフォントで入れ、**ユーザーがCapCut上で全選択→1本目と同じフォントに一括変更**する運用
- テロップは台本の行を1カード=1〜2行（1行〜10文字）に分割し、ナレーション尺内でオフセット指定。ffmpegはdrawtext（textfile=で日本語エスケープ回避・行ごとに別drawtextで中央揃え）
- **CapCutの2行テロップは「テロップ上」「テロップ下」の2テキストトラック**に行単位で載せる（同一トラック内の時間重複は禁止のため）
- **効果音は numpy で自作**（SE_don/whoosh/pop/kiran/sad.wav）。ffmpegでは adelay+amix、CapCutでは専用オーディオトラック。配置=場面転換whoosh・パンチラインdon・画面イン pop・落胆sad・前向きkiran
- **モザイク（サービス名を完全に伏せる場合）**: 前景を `scale=iw/18:-1:flags=area → 元サイズ:flags=neighbor` で全面ピクセル化（ぼかし帯より確実）
- **メモリ逼迫時の鉄則**: 4K HEVCの複数同時デコードはOOMで**黙って尺欠け**する（rc=0でも短い）。1クリップずつ変換→concat、x264は `preset veryfast + threads=2:lookahead-threads=1:rc-lookahead=10`、**出力尺=期待尺の検証+リトライ**を必ず入れる

## CapCut公式エフェクト辞書（2026-08-01確立）

ユーザーがCapCut上で一度使ったエフェクト類はドラフトJSONに実IDが記録される。それを採取した辞書が
`scripts/capcut_effect_dict.json`（フォント・花字・トランジション・動画エフェクト・ライブラリSEの完全なmaterial JSON）。
**新ドラフト生成時はこの辞書のmaterialを複製注入（idだけ新UUID）すれば、CapCut公式エフェクト付きで出せる。**

- テロップの正式フォント=**コーポレート・ロゴ（ラウンド）ver3 Bold**。TTF実体は `C:\Users\YutoM\Videos\リール素材\フォント\メインテロップ.ttf` → **ffmpeg焼き込みのdrawtextはこのTTFを使う**
- SEはCapCutライブラリの実音源mp3を `C:\Users\YutoM\Videos\リール素材\SE_CapCutライブラリ\` に確保済み（シャキーン系2種・どどん・ドーン・ピアノがーん）→ **numpy自作SEは廃止。焼き込みにもこのmp3を使う**
- 使い所（v5でのゆうとの実編集より）: ぐらつき=パンチライン／雨=心折れ／たなびく火=あきらめません／ホワイトパルス=感情反転の境界／花字CC4B=通常テロップ
- 辞書にないエフェクトを使いたくなったら、ユーザーにCapCutで一度使ってもらい、そのドラフトから再採取して辞書に追記する

## 素材の差し替え（ユーザーからの依頼対応）

「Driveの◯◯に変えて」と言われたら: ①素材を `C:\Users\YutoM\Videos\リール素材\<企画名>\` にコピー → ②capcut_export.py の SEGS の該当クリップ名を書き換え → ③再実行（allow_replace=Trueで上書き）→ ④CapCut再起動で反映。
**注意: ドラフト上書きはユーザーがCapCut上で加えた編集（テロップ等）を消す。** ユーザーが編集を始めた後は、上書きせず「差し替え素材を安定パスに置いて、CapCut上で右クリック→素材の置き換えをしてもらう」方式に切り替えるか、別名ドラフト（間借り編2_v2等）で出す。

## 検品（必須）

1. 各セグメントの出力尺 = 音声尺（±0.06s）をログで確認。
2. 完成版から10〜15点フレーム抽出→タイル画像を目視: セグメント境界のカット・ぼかし帯からのロゴはみ出し・フェードの効き・空フレーム（人物が画面外の瞬間）をチェック。
3. `ffmpeg -af ebur128 -f null -` でラウドネス実測（-16 LUFS目標）。
4. 納品: `G:\マイドライブ\50日企画素材\完成動画\` にコピーし、SendUserFileでユーザーにも送る。

## 落とし穴（2026-08-05 試作編1で判明・重要）

- **フォントのパスに日本語が入っているとffmpegが読めず、無言で標準ゴシックにフォールバックする。**
  `Fontconfig error: Cannot load default config file` が出ていても rc=0 で通ってしまうため気づけない。
  → **必ずフォントをASCIIパスにコピーしてから使う**（作業フォルダに `corp.ttf` としてコピーするのが確実）。
  レンダリング後は「太い丸ポップ体になっているか」を必ず目視確認する。
- **CapCutドラフトのSE・テロップは同一トラック内で時間が重なると SegmentOverlap で落ちる。**
  効果音は尾を引く音（ピアノがーん等5秒級）があるため、**トラックを複数用意して空いている方へ自動割当**する。
- **OPのテロップは1本目（５０日企画　１）の様式に合わせる**：上段y中心231・下段y中心1193・fontsize105・白字黒縁。
  内容は「◯日後に三宮に」／「スープ屋を開く大学生」。勝手に別様式（「あと◯日」等）にしない。
- **投票結果などのネタバレは、答えを言う瞬間まで出さない。**タメの無音区間を `silencedetect` で実測し、
  そこにドラムロールを敷いて、答えの瞬間に写真をバンッと出す。
