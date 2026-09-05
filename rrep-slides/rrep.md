---
marp: true
size: 16:9
paginate: true
html: true
---

<style>
:root{
  --ink:#1E2A22;
  --paper:#FBFAF6;
  --accent:#2F6B45;
  --warm:#C0533F;
  --muted:#7C7C72;
  --line:#E3E1D7;
  --mkgreen:#CDE7B4;
  --serif:"Yu Mincho","YuMincho","BIZ UDPMincho","Hiragino Mincho ProN",serif;
  --gothic:"Yu Gothic","YuGothic","BIZ UDPGothic","Meiryo",sans-serif;
}
section{
  width:1280px; height:720px;
  background:var(--paper);
  color:var(--ink);
  font-family:var(--gothic);
  font-size:26px;
  padding:70px 92px 76px 92px;
  position:relative;
  letter-spacing:.01em;
}
section::before{
  content:"農園 in the park";
  position:absolute; left:92px; bottom:34px;
  font-size:14px; letter-spacing:.18em; color:var(--muted);
}
section::after{
  right:92px; bottom:30px; left:auto; top:auto;
  color:var(--muted); font-size:14px; font-family:var(--serif); letter-spacing:.1em;
}
section.cover::before, section.cover::after,
section.divider::before, section.divider::after,
section.statement::before, section.statement::after,
section.message::before, section.message::after,
section.closing::before, section.closing::after{ content:""; display:none; }

.kicker{ display:flex; align-items:center; gap:14px; font-size:17px; font-weight:700;
  letter-spacing:.22em; color:var(--accent); margin-bottom:26px;}
.kicker::before{ content:""; width:38px; height:2px; background:var(--accent);}
.ctx{ font-size:17px; letter-spacing:.16em; color:var(--muted); font-weight:700; margin-bottom:22px;}
.ctx b{ color:var(--accent);}

h2{ font-family:var(--serif); font-weight:700; font-size:46px; line-height:1.4; margin:0 0 30px 0;}

.points{ list-style:none; padding:0; margin:0;}
.points li{ position:relative; padding-left:32px; margin:26px 0; font-size:31px; line-height:1.6; color:#2c352d;}
.points li::before{ content:""; position:absolute; left:0; top:16px; width:12px; height:12px; background:var(--accent); border-radius:50%;}

.mk{ background:linear-gradient(transparent 56%, var(--mkgreen) 56%, var(--mkgreen) 92%, transparent 92%); padding:0 3px; font-weight:700;}
.em{ color:var(--accent); font-weight:700;}

.row{ display:flex; gap:56px; align-items:center; margin-top:6px;}
.row .txt{ flex:1;}
.figure{ width:470px; flex:none;}
.figure img{ width:100%; height:380px; object-fit:cover; border-radius:2px;}
.cap{ font-size:16px; color:var(--muted); letter-spacing:.06em; margin-top:12px;}
.big-photo{ width:100%; height:420px; object-fit:cover; border-radius:2px; margin-top:8px;}

/* statement */
section.statement{ display:flex; flex-direction:column; justify-content:center; align-items:flex-start; padding:70px 120px;}
.eyebrow{ font-size:17px; letter-spacing:.24em; color:var(--muted); margin-bottom:28px; font-weight:700;}
.big{ font-family:var(--serif); font-size:52px; line-height:1.55; font-weight:700; letter-spacing:.02em;}
.after{ font-size:23px; color:var(--muted); margin-top:32px; letter-spacing:.03em;}

/* cover */
section.cover{ padding:0 120px; color:#fff; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;
  text-shadow:0 2px 16px rgba(0,0,0,.6);
  background:linear-gradient(0deg, rgba(10,14,11,.60), rgba(10,14,11,.50)), url("img/cover.png") center/cover no-repeat;}
.cover .eyebrow{ color:#ffffff; margin-bottom:22px;}
.cover .ctitle{ font-family:var(--serif); font-size:116px; font-weight:800; margin:0; line-height:1.02; color:#fff; letter-spacing:.01em;}
.cover .sub{ font-size:28px; margin-top:24px; color:rgba(255,255,255,.92); font-family:var(--serif);}
.cover .who{ font-size:18px; margin-top:40px; letter-spacing:.12em; color:rgba(255,255,255,.84);}

/* divider */
section.divider{ padding:0 100px; color:#fff; display:flex; flex-direction:column; justify-content:center;
  background:linear-gradient(0deg, rgba(11,16,12,.82), rgba(11,16,12,.60)), url("img/divider.png") center/cover no-repeat;}
.divider .dnum{ font-family:var(--serif); font-size:25px; letter-spacing:.32em; color:rgba(255,255,255,.74); margin-bottom:20px;}
.divider h2{ font-family:var(--serif); color:#fff; font-size:54px; margin:0 0 20px; line-height:1.35;}
.divider .sub{ color:rgba(255,255,255,.88); font-size:23px; letter-spacing:.03em;}

/* learn */
.lnum{ font-family:var(--serif); font-size:25px; color:var(--accent); letter-spacing:.24em; margin-bottom:16px;}
.tag{ display:inline-block; background:var(--accent); color:#fff; font-size:20px; font-weight:700; letter-spacing:.12em; padding:8px 24px; margin-bottom:26px;}
.headline{ font-family:var(--serif); font-size:50px; font-weight:700; line-height:1.45; max-width:1050px;}
.line{ font-family:var(--serif); font-size:44px; font-weight:700; line-height:1.5; margin:6px 0;}
.sub2{ font-size:26px; color:#4a4f47; margin-top:26px; line-height:1.6;}
.note{ font-size:22px; color:var(--muted); margin-top:26px;}

.chips{ display:flex; gap:18px; margin-top:36px; flex-wrap:wrap;}
.chip{ border:2px solid var(--line); border-radius:44px; padding:14px 30px; font-size:26px; font-weight:700; background:#fff;}

.tagred{ display:inline-block; background:var(--warm); color:#fff; font-size:22px; font-weight:700; padding:6px 22px; letter-spacing:.06em; margin-top:8px;}

.ba{ display:flex; align-items:center; gap:36px; margin:14px 0 8px;}
.ba .b{ font-family:var(--serif); font-size:40px; color:var(--muted); font-weight:700;}
.ba .arw{ font-size:44px; color:var(--accent);}
.ba .a{ font-family:var(--serif); font-size:52px; color:var(--accent); font-weight:700;}

.zero{ font-family:var(--serif); font-size:80px; font-weight:700; color:var(--muted); line-height:1;}
.grew{ font-family:var(--serif); font-size:80px; font-weight:700; color:var(--accent); line-height:1;}

/* timeline */
.tl{ display:flex; gap:22px; margin-top:10px;}
.tlitem{ flex:1; text-align:center;}
.tlitem img{ width:100%; height:300px; object-fit:cover; border-radius:2px;}
.tlitem .m{ margin-top:14px; font-family:var(--serif); font-size:28px; color:var(--accent); font-weight:700;}
.tlitem .n{ font-size:25px; font-weight:700; margin-top:2px;}

/* result */
.result{ display:flex; align-items:baseline; gap:28px; border-top:1px solid var(--line); padding-top:30px; margin-top:20px;}
.result .num{ font-family:var(--serif); font-size:88px; font-weight:700; color:var(--accent); line-height:1;}
.result .lbl{ font-size:26px; color:#39423a; line-height:1.6;}

/* summary + agenda rows */
.srow{ display:flex; align-items:baseline; gap:34px; padding:26px 0; border-top:1px solid var(--line);}
.srow:last-child{ border-bottom:1px solid var(--line);}
.srow .sn{ font-family:var(--serif); font-size:34px; color:var(--accent); width:58px; flex:none;}
.srow .sk{ font-size:30px; font-weight:700; width:320px; flex:none;}
.srow .sd{ font-size:26px; color:#4a4f47;}
.srow .sfull{ font-size:31px; color:#2c352d;}

/* message */
section.message{ padding:0 90px; color:#fff; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;
  background:linear-gradient(0deg, rgba(11,16,12,.74), rgba(11,16,12,.64)), url("img/message.png") center/cover no-repeat;}
section.message .big{ color:#fff; font-size:52px; line-height:1.55;}
section.message .after{ color:rgba(255,255,255,.88);}

/* closing */
section.closing{ background:var(--ink); color:#fff; display:flex; flex-direction:column; justify-content:center; align-items:center;}
.closing .thx{ font-family:var(--serif); font-size:62px; font-weight:700; letter-spacing:.05em;}
.closing .foot{ margin-top:30px; font-size:18px; letter-spacing:.12em; color:rgba(255,255,255,.72);}

.illu{ margin-top:20px;}
.duo{ display:flex; align-items:center; justify-content:center; gap:24px; margin-top:16px;}
.duocol{ width:500px; text-align:center;}
.duocol img{ width:100%; height:230px; object-fit:contain; background:#F4F0E4; border-radius:2px;}
.dlab{ font-size:25px; font-weight:700; margin-top:14px;}
.dlab .x{ color:#C0533F;}
.dlab .o{ color:#2F6B45;}
.duoarrow{ font-size:46px; color:#9a9a90;}
.trio{ display:flex; gap:22px; margin-top:18px;}
.triocol{ flex:1; text-align:center;}
.triocol img{ width:100%; height:206px; object-fit:contain; background:#F4F0E4; border-radius:2px;}
.tlab{ font-size:23px; font-weight:700; margin-top:14px;}
.tsub{ font-size:18px; color:#7C7C72; margin-top:6px; line-height:1.55;}
</style>

<!-- _class: cover -->
<!-- _paginate: false -->

<div class="eyebrow">RREP ｜ リーダーシップ概論</div>
<div class="ctitle" style="font-size:120px; line-height:1.02; font-weight:800;">農園 in the park</div>
<div class="sub">―― リーダーシップとチームビルディングについて</div>
<div class="who">兵庫県立大学　社会情報科学部　4年　松井優人</div>

---

<div class="kicker">AGENDA</div>

<h2>本日、お話しすること</h2>

<div class="srow"><div class="sn">01</div><div class="sfull">プロジェクトの概要</div></div>
<div class="srow"><div class="sn">02</div><div class="sfull">活動の軌跡と結果</div></div>
<div class="srow"><div class="sn">03</div><div class="sfull">チームビルディングとリーダーシップの学び</div></div>
<div class="srow"><div class="sn">04</div><div class="sfull">1年生へ伝えたいこと</div></div>

---

<!-- _class: statement -->
<!-- _paginate: false -->

<div class="eyebrow">はじめに、ちょっとだけ考えてみてください。</div>
<div class="big">
「良いチーム」「良いリーダーシップ」に<br>
必要なものって、<span class="em">何だろう？</span>
</div>
<div class="after">―― その答えは、最後にお話しします。</div>

---

<div class="kicker">01　PROJECT</div>

<div class="row">
<div class="txt">
<h2>舞台は、姫路の<br>御前山広場</h2>
<ul class="points">
<li>僕が<span class="mk">2年生のとき</span>のプロジェクト</li>
<li>大きなすべり台や丘のある、のびのびした広場</li>
<li>地域の方が<span class="mk">丁寧に手入れする</span>、素敵な場所でした</li>
</ul>
</div>
<div class="figure">
<img src="img/hiroba.png" alt="御前山広場">
<div class="cap">御前山広場（姫路市）</div>
</div>
</div>

---

<div class="kicker">01　PROJECT</div>

<h2>でも、ある問題を抱えていた</h2>

<div class="line">高齢化で、<span class="mk">公園を手入れする人がいなくなる。</span></div>
<div class="sub2">このままだと、地域が大切にしてきた広場が、<br>少しずつ元気をなくしてしまう。</div>

---

<!-- _class: statement -->

<div class="eyebrow">プロジェクトの、はじまり</div>
<div class="big">
こんな素敵な場所を、<br>
なくすのは<span class="em">イヤだ。</span><br>
<span class="mk" style="font-size:40px;">関心のあった農業分野とも結びつけて、なんとかできないか。</span>
</div>

---

<!-- _class: statement -->

<div class="eyebrow">CONCEPT</div>
<div class="big">
未来の<span class="em">"公園キーパー"</span>を、育てる。<br>
子どものときから、地域とともに、<br>
<span class="em">公園を好きになってもらう。</span>
</div>

---

<div class="kicker">01　PROJECT</div>

<h2>つまり、こんなプロジェクト</h2>

<div class="srow"><div class="sn" style="font-size:26px; width:130px;">目的</div><div class="sfull">子どもの頃の<span class="mk">「楽しい思い出」</span>で公園を好きになってもらい、<br>将来、公園をお手入れする人を育てる</div></div>
<div class="srow"><div class="sn" style="font-size:26px; width:130px;">手法</div><div class="sfull">大根の<span class="mk">種まき → 水やり → 収穫 → 鍋にして食べる</span>までを、<br>遊びも織り交ぜつつ、地域の方と一緒に一貫して体験するイベント</div></div>
<div class="srow"><div class="sn" style="font-size:26px; width:130px;">検証</div><div class="sfull">やって終わりにせず、<span class="mk">アンケートで効果を確認</span></div></div>

---

<div class="kicker">02　ACTION</div>

<h2>食育・菜園利活用・防災を軸に、半年間</h2>

<div class="tl" style="gap:26px;">
<div class="tlitem"><img src="img/t1_seed.png" style="height:300px;"><div class="m">9月</div><div class="n">種まき・水遊び</div></div>
<div class="tlitem"><img src="img/t2_sign.png" style="height:300px;"><div class="m">10月</div><div class="n">看板づくり</div></div>
<div class="tlitem"><img src="img/t3_sports.png" style="height:300px;"><div class="m">11月</div><div class="n">運動会・じょうろ工作</div></div>
</div>

---

<div class="kicker">02　RESULT</div>

<h2>そして最終イベント「防災鍋づくり」へ</h2>

<img class="big-photo" src="img/bousai.png" alt="防災鍋づくり 最終イベント" style="height:300px;">

<div class="sub2" style="margin-top:20px;"><span class="mk">みんなで一つの鍋を囲んだ。</span><br>アンケートの効果検証でも、活動の価値を裏づけられた。</div>

---

<!-- _class: divider -->
<!-- _paginate: false -->

<div class="dnum">03 ── LEARNINGS</div>
<h2>チームビルディング と リーダーシップ</h2>
<div class="sub">―― 失敗としんどさの中で、身についた3つの学び。</div>

---

<div class="lnum">LEARNING 01</div>
<div class="tag">チームビルディング</div>

<div class="headline">まず、<span class="mk">"戻れる軸"</span>＝<br>チームの共通目標を決める。</div>

---

<div class="ctx">学び① <b>チームビルディング</b></div>

<h2>実は、プロジェクトの序盤で<br>いきなり最大のピンチ。</h2>

<div class="line">予定していた<span class="mk">実施許可が、下りなかった。</span></div>
<div><span class="tagred">＝ そもそも、始められない</span></div>

---

<div class="ctx">学び① <b>チームビルディング</b></div>

<div class="line">それでも、誰一人<br><span class="mk">「別の公園でやろう」とは言わなかった。</span></div>

<div class="sub2">最初に“戻れる軸”を決めていたから、ブレずに前を向けた。</div>

<div class="ba">
<div class="b">「無理かも…」</div>
<div class="arw">→</div>
<div class="a">「絶対、ここでやる」</div>
</div>

---

<div class="lnum">LEARNING 02</div>
<div class="tag">リーダーシップ</div>

<div class="headline">リーダーシップとは、<span class="mk">"率先して動く"</span>こと。<br>みんなが動ける<span class="mk">"役割分担"</span>をつくること。</div>

<div class="duo">
<div class="duocol"><img src="img/illus_pyramid.png" alt="頂点で指示する人"><div class="dlab"><span class="x">✕</span> 頂点で指示する人</div></div>
<div class="duoarrow">→</div>
<div class="duocol"><img src="img/illus_gear.png" alt="歯車の中心で回す人"><div class="dlab"><span class="o">◯</span> 歯車の“中心”で回す人</div></div>
</div>

---

<div class="ctx">学び② <b>リーダーシップ</b></div>

<h2>許可が下りるまで、<br>本当にしんどかった。</h2>

<div class="trio">
<div class="triocol"><img src="img/illus_night.png" alt="連日の深夜MTG"><div class="tlab">連日の深夜MTG</div><div class="tsub">終わる時間を決めずに、話し込んでいた</div></div>
<div class="triocol"><img src="img/illus_clash.png" alt="情報共有のすれ違い"><div class="tlab">情報共有のすれ違い</div><div class="tsub">議事録が足りず、参加できなかった人が置いていかれる</div></div>
<div class="triocol"><img src="img/illus_heat.png" alt="メンバーの熱量の違い"><div class="tlab">メンバーの熱量の違い</div><div class="tsub">事情も温度感も、人それぞれ</div></div>
</div>

<div class="sub2" style="margin-top:24px; text-align:center;">それでも、誰かが<span class="mk">率先して動く</span>ことで、チームは止まらなかった。</div>

---

<div class="lnum">LEARNING 03</div>
<div class="tag">対話と検証</div>

<div class="headline"><span class="mk">失敗を恐れず</span>、<br>早めの対話で構想を深める。</div>

---

<div class="ctx">学び③ <b>対話と検証</b></div>

<h2>決まる前から、<br>地域に相談し続けた。</h2>

<div class="sub2">その積み重ねで<span class="mk">信頼</span>が生まれ、<br>地域の方・市議さんが、実現の道を開いてくれた。</div>

---

<div class="ctx">学び③ <b>対話と検証</b></div>

<div class="line">「活動できる」と決まった瞬間、<span class="em">空気が一変。</span></div>
<div class="sub2" style="margin-top:14px;">ここからは<span class="mk">役割分担</span>でチームがフル稼働 ―― 姫路に近いメンバーは畑の水やりへ。<br>チラシづくり、イベント企画、地域への説明も、それぞれの担当に。</div>

<div class="line" style="margin-top:34px;"><span class="mk">表面的な仲良しじゃない、“本物のチーム”へ。</span></div>

---

<div class="ctx">学び③ <b>対話と検証</b></div>

<h2>失敗しても、分析して、やり直す。</h2>

<div class="ba">
<div class="zero">参加者 0人</div>
<div class="arw">→</div>
<div class="grew">50人以上</div>
</div>
<div class="sub2">「伝え方と場所が悪かった」と見直して、再設計。<br><span class="mk">チームだけでなく地域とも対話しながら考え抜く</span>ことが、構想を前に進めた。</div>

---

<div class="kicker">04　SUMMARY</div>

<h2>最初の問いの答え ＝ 3つの学び</h2>

<div class="sub2" style="margin-top:0;">良いチーム・良いリーダーシップに必要なものは――</div>
<div class="line" style="margin-top:14px;">① <span class="mk">戻れる共通の目標</span></div>
<div class="line">② <span class="mk">率先して動き、役割分担をつくる</span></div>
<div class="line">③ <span class="mk">失敗して、対話して、やり直す</span></div>

<div style="font-family:var(--serif); font-size:31px; font-weight:700; margin-top:30px; padding-top:22px; border-top:1px solid var(--line);">この苦労も、成功体験も —— <span class="mk">他のどんな授業でも得られない。</span></div>

---

<!-- _class: message -->
<!-- _paginate: false -->

<div class="big">
その辛さを越えた分だけ、<br>力は本物になる。
</div>
<div class="after">一つでも「やりきった」と言える経験を。ぜひ、RREPへ。</div>
