# 共有版に「入れなかったもの」一覧（代表確認用・2026-09-04）

代表PCのClaude記憶（44ファイル）と作業フォルダから、以下は意図的に除外した。

## 1. 代表個人に関するもの（団体の知識ではない）
| 元ファイル | 内容 |
|---|---|
| project_career_decision | 進路選択（就職先の比較） |
| project_life_roadmap | 人生のロードマップ（2026〜2036） |
| project_sasashima_lab | 卒業研究 |
| project_agri_failure_ontology_ai | 個人の事業構想（Notion非掲載指示あり） |
| project_english_coach / project_futari_calendar | 個人用アプリ |
| user_yuto_profile の大半 | 学部・インターン先・就活状況など。団体として共有してよいビジョン部分のみ 08_history_lessons.md に転記 |

## 2. 外部企業との個別の関係
| 元ファイル | 扱い |
|---|---|
| feedback_iobi_model / project_iobi_go_decision / project_iobi_regions / feedback_no_iobi_in_notion | 「りふぁーむNotionには書かない」指示に準じ、共有版にも一切書かない。「勝ち筋が見えない」等の学びは「外部経営者の指摘」として匿名化して記載 |
| feedback_slide_design のIOBI部分 | /slide（赤基調テンプレ）自体を共有版に含めない |

## 3. 秘密情報（見つけた場所を明記。**代表側で対処推奨**）
| 場所 | 内容 | 推奨 |
|---|---|---|
| `.claude/settings.local.json`（元フォルダ） | Railway PostgreSQL のパスワードが許可コマンド文字列に平文で残っている（`PGPASSWORD=...`） | 共有版には含めていない。**Railway側でパスワードをローテーションし、該当行を削除** |
| `vegedasheep_images/generate.py` | Google（Gemini）APIキーが直書き | 共有版 `tools/generate_image.py` は環境変数 `GEMINI_API_KEY` 方式に変更済み。**元のキーは再発行推奨** |
| 記憶 project_hp_renewal | HP管理画面のパスワード | 共有版には書かず「代表管理」と記載 |
| 記憶 project_soup_app_design | 管理画面の初期ログイン・Stripe鍵・DB接続文字列の露出履歴 | 共有版には書かず、ローテーション推奨の注記のみ |
| 記憶 project_soup_app_design | GitHub PAT を平文で `.git-credentials` に保存している旨 | 共有版には書かない |

## 4. 代表PCの環境に依存するもの（他のPCでは動かない）
| 元 | 扱い |
|---|---|
| `.claude/skills/reel-build/`（リール自動生成。CapCutのローカルパス・Videosフォルダ前提） | 含めない。テロップ様式・教訓だけ 04_brand_creative.md に転記 |
| `reels/`・`vegeone_brand/`・`vegeone_nobori/`・`soup-cup-mockups/` の実データ | 含めない（サイズ大・生成物）。所在だけ記載 |
| `.claude/launch.json`（各アプリの開発サーバー設定） | 含めない。アプリのリポジトリは別（07_systems.md 参照） |
| `.company/`（秘書・仮想組織システム。2026-06-01時点の古い体制のまま） | 含めない。内容は 01_organization.md に最新化して吸収 |
| scheduled task「soup-weekly-minutes」 | 代表PCでのみ動く。存在だけ記載 |
| `/weekly-surinagashi`（非推奨スキル）、`/slide`（IOBI用） | 含めない |
| `rrep-slides/img/`（48MB） | 含めない。見本 rrep.md の画像は各自で用意 |

## 5. 共有版で「直した」もの（元の記述が古かった）
| 場所 | 修正 |
|---|---|
| `/soup-recipe` の制約 | 「肉不使用」→「ベースは植物性・蒸し鶏トッピングのみ可（2026-07-12）」。「仕込み＝レンタルキッチン」→「三宮の間借り厨房のみ・レンタルキッチン不使用（2026-07-12）」 |
| `/flyer` `/soup-recipe` `dev-orchestra` | 代表PCの絶対パス（C:\Users\YutoM\...）を相対パスに変更 |
| `.company/CLAUDE.md` の「すりながし最優先」「まいへ代表移譲」等 | 共有版では 2026-07 以降の決定で上書き |

## 6. 判断に迷ったので入れたもの（不要なら削除してください）
- メンバーの名前（ニックネーム）と担当。団体内共有なら問題ないと判断
- 農家リスト（屋号のみ。連絡先・口座は含めない）
- LIFF ID・Cloudinary の cloud name（URLに露出する公開値のため）
- 店舗の住所・営業時間・価格（公開情報）
