# プロンプトの型（英語で書く。日本語でも通るが英語の方が安定）

## 3-1. 商品素材（グリーンバック）
実物写真を1枚渡す。
```
Recreate this image exactly（器・中身・トッピングを具体的に書く）but replace the background with a flat, uniform, bright pure GREEN screen (#00FF00), no gradient and NO shadow on the green. Keep the food identical, realistic photo look, natural grain. No text, no logo.
```
実物を直してから素材化するとき（トッピング差し替えなど）：
```
Keep the cup, the logo, the soup and the lighting exactly as they are. Changes: (1) remove the shredded seaweed; (2) add two glossy candied sweet potato chunks and one round black-sesame rice cracker on the rim. Background: flat pure GREEN (#00FF00). Natural grain, slightly matte, smartphone-photo look, not CGI. No text other than the logo.
```

## 3-2. 1枚の絵として生成（手本2枚＋商品素材）
渡す順番＝手本1・手本2・商品素材1・商品素材2。番号で指す。
```
STYLE: Follow the look of the first two reference images (a Japanese coffee chain's autumn campaign key visual): a bright warm golden-orange gradient background, the product HUGE in the foreground filling about 60 percent of the frame, a GIANT roasted sweet potato split open behind it with glossy amber syrup dripping down, a few autumn leaves, small syrup splashes. Everything is one cohesive advertising composite with consistent lighting, NOT cutouts placed on a table. Portrait 4:5. Leave the top 20 percent calmer for a headline. NO text, NO letters, NO logos except the small VEGEONE label on the white cup. Do NOT draw any coffee chain logo.
PRODUCTS: Use the kraft-brown paper bowl of chunky candied sweet potato with whipped cream from the THIRD image as the hero at front-left, large and slightly tilted. Behind it to the right, the white VEGEONE cup of golden potage from the FOURTH image, a bit smaller. Keep both products faithful to the references.
```
構図を変えたいとき：自作の絵は参考に入れず、「LAYOUT (must follow exactly): ... is at the LEFT side and is the FRONT-MOST object ...」と位置と前後を言葉で指定する。

## 3-3. 部分だけ直す（例：イラスト風の葉を写真に）
元絵を1枚渡す。
```
Edit this image. Keep EVERYTHING exactly as it is (the giant split roasted sweet potato, the syrup, the kraft bowl, the white VEGEONE cup, the background, composition and lighting). Change ONLY the maple leaves: replace every illustrated, flat maple leaf with REAL photographic autumn Japanese maple leaves in red, orange and yellow, with natural veins, slight curl and soft shadows. Same positions and sizes. No text.
```

## 3-4. 黒板の背景（手書き風看板用）
```
A realistic photograph of a dark green-black chalkboard menu board, slightly dusty. Hand-drawn WHITE CHALK decorations ONLY along the left and right edges and in the two BOTTOM corners: a simple double-line chalk border frame with small flourishes, maple leaves and sparkles in the bottom corners, a small chalk drawing of a split roasted sweet potato at the bottom-left and a small steaming soup cup (open cup, no lid) at the bottom-right. The TOP 40 percent and the whole CENTER must be completely EMPTY board surface. No text, no letters, no numbers. Charming cafe-menu chalk style. Portrait 3:4.
```

## 3-5. のぼり用の縦長の絵（9:16）
手本1枚＋本番の絵（4:5）を渡す。
```
Create a tall portrait 9:16 image in the same style and color as the second reference image (our key visual). Put the whole group of products and the sweet potato in the LOWER 45 percent of the frame, and make the UPPER 55 percent a plain, smooth golden-orange gradient with only a thin stream of syrup falling from the top, so that large vertical text can be placed there. Keep the products faithful to the reference. No text, no letters, no logos except the VEGEONE label.
```

## 3-6. のぼり用・写真フルブリード（スタバのストロベリーバナーの型）
手本（`reference/examples/nobori_starbucks_strawberry_fullbleed.jpg`）＋商品素材を渡す。
```
Design a tall portrait 9:16 banner photo in the style of the FIRST reference image (the background is filled EDGE TO EDGE with the ingredient itself, the product is huge in the center, bright and appetizing, nothing is left empty). Our version: the whole background is densely filled with glossy chunks of candied sweet potato with amber glaze and black sesame, slightly out of focus toward the edges. In the center, large, the kraft-brown bowl of candied sweet potato with whipped cream from the SECOND reference image, sharp and glossy. Leave the top 12 percent and the bottom 22 percent a little calmer so text can be placed. Photographic, one cohesive image. NO text, NO letters, NO logos.
```
出来た9:16を上下に反転ぼかしで延長して1:3にする（`scripts/nobori_full.py`）。

## やってはいけない頼み方
- 文字を描かせる（日本語は崩れる）
- 「もっとおしゃれに」「いい感じに」（基準がない → 手本を渡す）
- 一度に5つ直す（別の絵になる）
- 自作の途中の絵を参考に入れて構図を変えようとする（引っ張られる）
- 「背景を消して」だけ（効きにくい → グリーンバックで出し直す）
