# 07 システム（soup-app／okaeri-noen／HP）・保守体制・開発方針

**秘密情報（パスワード・APIキー・DB接続文字列・管理画面のログイン情報）はここに書かない。** 代表が管理。各自は環境変数で持つ。

## 2026-10-31時点の注意（閉店に向けて）
- soup-app・公式LINEの有料プラン・HP は**当面ゆうとが費用を負担して残す**（期限未定・2026-10-05）。アプリの保守もゆうとに残っている
- **三宮の店は2026-11-26で閉店**、11月は木曜のみ 11:00〜14:00。soup-app の営業日表示（`client/src/data/business.js`、2026-09-24設定）と HP `/soup`（ページの案内・構造化データ、2026-10-05更新）は「月・火・木 11:00〜14:00」のまま（2026-10-31に代表PCのローカルリポジトリで確認。本番も同じかは未確認）。11月の営業日と閉店の反映が必要。Googleマップ（ビジネスプロフィール）・食べログの表示も同様に未確認
- 閉店後も公式LINE・Instagram（@refarm_soup）は出店の告知に使う（10/16版）

## 保守体制＝バイブコーディング（2026-07-06確認）
- 学生メンバーはClaude Codeを使えず、コードを触れる人もいない前提
- 学生が触るのは**管理画面・LINE・Notion・フォームのみ**。日常運用の変更（メニュー・価格・スロット・拠点・お知らせ）はすべて管理画面のマスタ機能に押し込む
- **AIが自走する設計**（代表明言）。プロンプト→AI修正→自動デプロイまで人間の承認を挟まない。トラブル時は代表が対応。「AIだけで運営が回ること自体を実証したい」→**人間承認ステップを提案しない**
- **修正依頼フォーム**＝soup-app の `/admin` →「修正依頼」タブ（対象サイト＝スープアプリ／おかえり農園／HP／その他）。学生は自然文＋緊急度＋発生画面で送信→代表がその依頼文をClaude Codeに投げて修正・デプロイ。おかえり農園に別のadminを作る案は保留（当面このプルダウンで集約）
- Skillsも自走前提（質問で止まらない、情報がなければ「記録なし」）

## 開発方針＝オーケストラ開発（2026-07-12）
中〜大規模の実装は `.claude/skills/dev-orchestra/SKILL.md` の手順：上位モデル（fable/opus）がスペック作成→sonnet（`impl-exec` エージェント）が実装・自己検証→上位モデルが全差分レビュー・検証再実行・コミット。品質はスペックの粒度と指揮官のレビューで担保。小さな修正は直接でよい。

## 1. soup-app（VEGEONE 注文アプリ・管理画面）
- GitHub: `YutoMatui/refarm-soup-app`（private）。ローカルは代表PC `refarm-cc-company/soup-app`
- スタック：フロント React+Vite（Vercel、Root=client）／バック FastAPI+SQLAlchemy（Railway、Root=api、Dockerfile）／DB Railway PostgreSQL（スキーマ `soup`）／決済 Stripe／通知 LINE Messaging API／画像 Cloudinary（cloud `dcexzyhh7`、preset `soup_unsigned`）
- 本番：フロント https://refarm-soup-app.vercel.app ／API https://refarm-soup-app-production.up.railway.app 。Vercelの `client/vercel.json` で `/api/*` をRailwayへ転送
- LIFF ID `2010581177-PdAMan24`（Channel ID 2010581156）。リッチメニュー各セル＝ `https://liff.line.me/2010581177-PdAMan24/{menu|/|mypage|points}`
- 顧客画面：C1ホーム→C2メニュー→C3商品詳細→C4カート→C5受け取り（スロット排他制御）→注文完了／C10健康レポート／`/subscribe`（朝ベジ会員 Stripe Billing）／`/mypage`（デジタル会員証・LINEログイン）
- 管理画面 `/admin`：売上ダッシュボード・注文一覧・メニュー編集CRUD・サブスク会員数・**メニュー台帳**タブ・修正依頼。2026-09〜10に追加＝**レジ**（店頭会計・セットのスープとサイズ選択・クーポンコード割引・出店用のレジ専用商品）／**来店・リピート**（来店人数・杯数・客単価・リピート率）／**常連グレード**（ブロンズ・シルバー・ゴールド・プラチナ）／「また来てくれない理由」アンケート（公式LINEから回答）／みんなの日報／**経営管理**（収支・勘定科目で記録する経費・立替の承認と精算・キャッシュ台帳。承認した領収書は Googleドライブの月別フォルダへ自動保存）。タブは「ダッシュボード／メニュー／お店・お客様／お金／管理」にまとめた（2026-10）
- 2026-09に止めたもの：**デリバリー一式（注文・共同購入・配達枠・シフトのデリバリー役・`/admin/deliveries`）は2026-09-21に削除**／モーニング・冷製は10月から表示しない／農家在庫タブは外した
- 栄養の正＝`client/src/data/nutrition.js`（原則読み取り専用。食材マスタ・1食基準・合格ライン・調理ロス係数・PRESET_RECIPES）。seed生成＝`tools/gen_seed_nutrition.mjs`→`api` の `seed.py`
- UIクラス：管理＝`adm-*`／消費者＝`screen`系。管理UIは横文字を使わない（「予約なし来店」等）
- 未実装（2026-07時点の記録）：サブスクと会員／注文履歴の紐付け・Stripe Webhook本番登録・ポイント／紹介・スロット管理。※共同購入・拠点マスタ・便編成はデリバリー終了で不要に、店頭会計はレジとして実装済み（2026-09）。そのほかの項目の現状は未確認
- 注意：本番のADMINパスワードは初期値から変更が必要と記録あり（代表確認事項）。Stripe鍵・DB接続文字列はチャットで露出したことがありローテーション推奨

## 2. okaeri-noen（おかえり農園 会員LIFF＋管理）
- GitHub: `YutoMatui/okaeri-noen`（private）。本番 https://okaeri-noen.vercel.app ／Railway API稼働
- スタックは soup-app に準拠（React+Vite／FastAPI・SQLiteフォールバック付き／PostgreSQL／LINE Messaging API+LIFF）。**決済はカード廃止・現金／振込のみ**（Stripe不要）。写真は自前バックエンド保存（Cloudinary不要）
- LINE Messaging APIチャネル ID 2010581557／LIFF ID `2010581570-NszQZXQj`（LINEログインチャネル 2010581570）
- 会員LIFF 9画面＋管理画面4タブ。全フロー検証済み（登録→予約→チェックイン→記録→承認→畑だより→ありがとう→アンケート集計→現金消込）。push 200通/月制約。AIはオプション
- 要件定義書の控え＝代表PC `okaeri-noen/要件定義書.md`。セットアップ手順＝同 `README.md`

## 3. refarm-hp（公式HP）
- **正のURL＝ https://www.refarmkobe.com **（2026-09-04 DNS載せ替え完了。refarmkobe.com→www へ308転送。旧 refarm-hp.vercel.app も www へ転送）
- GitHub: `YutoMatui/refarm-hp`（private）。Vercel（アカウント refarmkobe-9940／チーム refarm-ff84e7d8）と Git 連携済み
- スタック：Next.js + Vercel。更新コンテンツは `content/` 配下の md/JSON（`site.json`＝公式LINE URL・広告コンバージョンラベル等、`media.json`＝画像割り当て、`hero/`＝ヒーロー画像）
- 構成：トップ（振り分け・循環図）／`/okaeri`（会費 月4,000円・2026-09-26更新）／`/okaeri/setsumeikai`（説明会）／`/soup`（Google広告LP。店舗情報・注文方法・「飲むことが地域の応援になる」・Googleマップ・ギャラリー）／`/soup/ingredients`（食材こだわり）／`/contact`。`/soup/spot`（お届けスポット）はデリバリー終了で2026-09-21に外した
- **AI管理画面 `/admin`**（パスワードは代表管理）：メンバーが日本語で指示→Claude API が `content/` の変更案生成→プレビュー→反映（GitHubへ自動コミット→Vercel自動デプロイ。1編集≒5〜15円）。「写真・動画」タブ＝Cloudinary（cloud `r8y4etju`、フォルダ `refarm-hp`）へアップロード→14スロットに割り当て。**文章編集・写真差し替え・本番反映がメンバーだけで完結する**
- お問い合わせフォーム＝`/api/contact`→Gmailアプリパスワード直送（nodemailer）で refarmkobe@gmail.com へ。Gmailアドレスは公開ページに載せない
- SEO（2026-09-04）：`src/lib/seo.ts`・robots・sitemap・canonical＋OGP・JSON-LD（Organization／Restaurant：加納町3-11-8 2階。営業時間は2026-10-05に「月・火・木 11:00〜14:00」へ更新済み、11月と閉店は未反映）・旧Wix 19URL→301転送
- Google広告：gtag `AW-18359764456` 全ページ設置。LINEボタンが `line_click` イベント＋コンバージョン送信。コンバージョンラベルは `content/site.json` の `adsConversionLabel`
- 残タスク（代表本人）：Search Console登録＋sitemap送信、Wixサイトプラン解約（ドメイン契約は維持）、Google広告の最終URL・Instagram/LINEのリンクを www に更新。`stats.json` の数字（20軒/50種/3年）は仮
- 開発サーバーがメモリ不足で落ちやすい→ローカル検証が不安定なときは push→本番で検証
- 旧サブドメイン：app.refarmkobe.com（ベジコベ）・lp.refarmkobe.com は別プロジェクトのまま

## 4. ベジコベ（撤退済み・稼働中）
代表自作のLINE受発注アプリ（農家の請求書・発注作業をカット）。app.refarmkobe.com。消費者向け販売は撤退したが、農家DB（19軒）・年間カレンダーの元データとして残る。

## 5. 自動化（代表PCで動作）
- scheduled task「soup-weekly-minutes」：毎週水曜12時にスープ議事録の下書きを 🗓 スープ議事録DB に作成。**2026-08-25からはタスクボードを列挙しない形**＝「📊 今週の数字（直近営業日の実売・現金残・損益分岐）」「📋 今日の議題（決めたいこと中心・関連ページへのリンク）」「✅ 今日決まったこと」「📮 次回まで（担当と期限だけ）」。前回の議事録の「決まったこと」「次回まで」から未決の論点を拾う
- タスクボードを見るときは現行の単月黒字ボード（`ee09fc4a-...`）。旧ボード `1b291268-...` は2026-09-10からアーカイブ扱い、`ff073b70-...` は絶対に使わない（`06_notion_map.md`）
- 定期タスク `weekly-leader-meeting-prep`（毎週月曜）：リーダー会が2026-10-01に廃止されたため、ページを作らず報告だけで終わる扱い（2026-10-27時点）。止めるか全体定例用に作り直すかは代表の判断待ち
- スープの週次まとめ（スープ議事録DBの「週次まとめ」）は自動で作られているが、タイトルが旧名「すりながしチーム 週次まとめ」になっている（2026-10時点）。作っている仕組みの場所はこのリポジトリでは未確認
