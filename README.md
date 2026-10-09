# refarm-claude — りふぁーむの知識を入れたClaudeを、全員・どこからでも使うためのリポジトリ

このリポジトリを開いた Claude Code は、`CLAUDE.md` と `knowledge/` を読んで
りふぁーむの事業・ルール・Notionの場所を把握した状態で会話を始めます。
`/flyer` `/soup-recipe` `/leader-meeting-prep` などのスキルも一緒に配布されます。

```
refarm-claude/
├── CLAUDE.md              ← 最初に読まれる「頭」。会話ルール・事業の全体像・判断の原則
├── knowledge/             ← 詳しい記憶（話題ごとに Claude が読みに行く）
│   ├── 01_organization.md      体制・引継ぎ・リーダー会・経費
│   ├── 02_soup_business.md     スープ事業の戦略・価格・店舗・デリバリー・営業
│   ├── 03_soup_nutrition_recipe.md  レシピ開発・栄養設計・管理栄養士監修
│   ├── 04_brand_creative.md    VEGEONEロゴ・のぼり・デザイン・スライド・リール
│   ├── 05_okaeri_noen.md       おかえり農園
│   ├── 06_notion_map.md        NotionのID・置き場所ルール
│   ├── 07_systems.md           アプリ・HP・保守体制
│   └── 08_history_lessons.md   創業の歩み・撤退の学び
├── .claude/
│   ├── commands/          ← スキル（/flyer /refarm-slide /soup-recipe /research /leader-meeting-prep /weekly-team-report）
│   ├── agents/impl-exec.md
│   ├── skills/dev-orchestra/
│   ├── skills/reel-capcut/    ← 台本→CapCutドラフト（メンバーが動画を作る入口）
│   ├── skills/reel-build/     ← 完成mp4まで焼き込むときの詳細手順
│   ├── skills/creative-kv/    ← 販促ビジュアル（広告4:5・A型看板・のぼり）。手本画像・発注書・SETUP.md 入り
│   └── settings.json      ← Notion等の許可設定（秘密情報なし）
├── slides/themes/         ← /refarm-slide のテーマCSS
├── rrep-slides/rrep.md    ← スライドの見本
├── flyers/                ← チラシの見本2枚
├── vegeone_nobori/        ← のぼりの骨格（nobori_line.py）と差し替え版（nobori_imo_gold.py）。PDFはChrome headlessで出力
├── vegeone_brand/build_print.py ← VEGEONEロゴをコードで描く部品
├── fonts/                 ← のぼり用フォント（Zen Maru Gothic・Dela Gothic One、OFL）
└── tools/generate_image.py ← Gemini画像生成（GEMINI_API_KEY が必要）
```

---

## A. メンバーのPCで使う（Claude Code デスクトップ）

1. Claude デスクトップアプリをインストールし、りふぁーむ用のClaudeアカウントでログインする
2. GitHub Desktop（または `git`）でこのリポジトリを clone する
   ```bash
   git clone https://github.com/<org>/refarm-claude.git
   ```
3. Claude アプリの「Code」タブで、clone したフォルダを開く
4. 最初に「りふぁーむについて知っていることを3行で教えて」と聞いて、知識が入っていることを確認する
5. **Notion を使うスキル**（/leader-meeting-prep 等）を使う人は、Claude の設定 → コネクタ から Notion を接続する（各自1回だけ）
6. 知識が更新されたら GitHub Desktop で「Pull」を押す（週1回で十分）

## B. スマホ・外出先から使う（代表向け）

| 方法 | 仕組み | できること | 条件 |
|---|---|---|---|
| **1. Claude Code on the web** | claude.ai/code で GitHub を接続し、このリポジトリを選んでクラウド上のサンドボックスで作業する。スマホのClaudeアプリ「Code」タブから同じクラウドセッションを見て操作できる | リポジトリを clone して動くので CLAUDE.md・knowledge・スキルが効く（※CLAUDE.md や .claude/ の読み込みは公式ドキュメントに明記がないため、初回に「りふぁーむについて3行で」と聞いて確認する） | GitHub にこのリポジトリを push しておく。初回に GitHub アプリ連携を許可。Notion コネクタが使えるかは**未確認**（使えない場合は方法2） |
| **2. Remote Control（PCが起動しているとき）** | 自宅PCで `claude remote-control` を実行（または既存セッションで `/remote-control`）し、スマホのClaudeアプリ「Code」タブから操作する | PC上の全ファイル・ローカルのMCP（Notion等）・記憶領域まで全部使える。今の環境と完全に同じ | Pro/Max 等のサブスク、claude.ai ログイン、PCが起動していること。公式: https://code.claude.com/docs/en/remote-control.md |
| 3. Claude.ai プロジェクト | claude.ai で「プロジェクト」を作り、CLAUDE.md と knowledge/*.md をナレッジとしてアップロード | 会話・相談・文章作成 | スキルやファイル操作は使えない。ファイル更新時に再アップロード |

**公式ドキュメントで確認済みの事実**: Claude Code の自動メモリ（`~/.claude/projects/.../memory/`）は**PC固有で、クラウド環境や別PCには同期されない**（https://code.claude.com/docs/en/memory.md）。だからこそ、このリポジトリの CLAUDE.md / knowledge/ に書き出す必要があります。

**使い分けの目安**: 外出先で代表が「今の自分のClaude」をそのまま使いたい→方法2。メンバー共有＋PCが起動していなくても使いたい→方法1。

## C. 知識の更新ルール

- 事業の決定・方針転換があったら `knowledge/` の該当ファイルに **日付つきで追記**する（上書きしない。古い判断は「経緯」として残す）
- 更新は代表または各チームリーダーが行い、GitHub に push する
- Claude に「この決定を knowledge に反映して」と頼めば下書きしてくれる
- **書いてはいけないもの**: パスワード・APIキー・DB接続文字列・個人の口座情報・団体外の個別交渉

## D. 各スキルに必要なもの

| スキル | 追加で必要なもの |
|---|---|
| /flyer | Google Chrome（PDF化に使う）。写真生成は `GEMINI_API_KEY` |
| /refarm-slide | Node.js（`npx @marp-team/marp-cli`） |
| /soup-recipe | soup-app リポジトリをこのリポジトリの隣に clone（無い場合は概算モードで動く） |
| /research /leader-meeting-prep /weekly-team-report | Notion コネクタ |
| dev-orchestra | 対象リポジトリ（soup-app / okaeri-noen / refarm-hp）へのアクセス権 |
| reel-capcut | CapCutデスクトップ版・Googleドライブ（パソコン版）・ffmpeg・`pip install pyJianYingDraft`。生成AIを使う場合のみ `GEMINI_API_KEY`。**手順は `.claude/skills/reel-capcut/reference/setup.md`** |
| reel-build | reel-capcut と同じ（完成mp4まで書き出すとき用） |

---

## E. 動画づくり（reel-capcut）

Notionの台本を渡すと、Driveから素材と録音を探して **CapCutで開けるドラフト** にして返します。
メンバー向けの使い方は Notion の
[🎬 Claudeで動画をつくる（メンバー用マニュアル）](https://app.notion.com/p/3d291268b8988181bc8ededd22cf4595) を見てください。

**お金がかかる操作があります。** 素材が足りないカットを画像から動画にする機能は
1本（8秒）約180円です。次の歯止めを入れてあります。

- 生成の前に金額を提示し、**月の上限（既定3,000円）を超えるものは実行前に止まる**
- だれが・いつ・何に・いくら使ったかを、Drive上の共有台帳
  `G:\マイドライブ\50日企画素材\_API利用ログ.jsonl` に全員ぶん記録する
- 「今月のAPI利用いくら？」と聞けば、人ごと・モデルごとの内訳が出る

台帳に載るのはこのスキル経由の分だけです。**本当の請求は Google Cloud Console →
お支払い → レポート（SKU別）が正**なので、月末に必ず突き合わせてください。
誰の分か請求側で分けたいときは、メンバーごとに別のAPIキーを発行します。
