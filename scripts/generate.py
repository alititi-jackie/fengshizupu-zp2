#!/usr/bin/env python3
"""Generate the zp2 static site (各地冯氏族谱收藏) into ./site.

Chrome (header/nav/footer) mirrors fengshizupu.com; styles come from the
shared assets/genealogy-theme.css (source of truth: main site repo
public/assets/genealogy-theme.css) plus assets/style.css carried over from
the Enping site. The reader reuses the Enping continuous-scroll reader
(reader-controls.js + volume-reader.js).
"""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site")
DOMAIN = "https://zp2.fengshizupu.com"
MAIN = "https://fengshizupu.com"
THEME_V = "08b0b6543950"

FAB_SCRIPT = """
<script>
var ft = document.getElementById('fabTop');
function fabShow(){ ft.classList.toggle('on', window.scrollY > 900); }
window.addEventListener('scroll', fabShow, {passive: true}); fabShow();
ft.onclick = function(){ window.scrollTo({top: 0, behavior: 'smooth'}); };
function sharePage(){ var u = location.href, t = document.title;
  var description = document.querySelector('meta[name="description"]').content;
  if (navigator.share) { navigator.share({title: t, text: description, url: u}).catch(function(){}); }
  else if (navigator.clipboard) { navigator.clipboard.writeText(u).then(function(){
    var w = document.querySelector('.share-wrap'); if (!w) return;
    var el = w.querySelector('.share-toast');
    if (!el) { el = document.createElement('span'); el.className = 'share-toast'; el.textContent = '链接已复制'; w.appendChild(el); }
    el.style.display = 'block'; setTimeout(function(){ el.style.display = 'none'; }, 1600);
  }); } }
</script>"""

SVG_BACK = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 19-7-7 7-7"></path><path d="M19 12H5"></path></svg>'
SVG_TOP = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 7-7 7 7"></path><path d="M12 19V5"></path></svg>'
FAB = """<div class="fab"><button id="fabTop" type="button" title="回到顶部" aria-label="回到顶部">""" + SVG_TOP + """</button><button id="fabBack" type="button" title="返回" aria-label="返回" onclick="history.back()">""" + SVG_BACK + """</button></div>"""


def head(title, desc, extra_css="", path="/"):
    og_url = DOMAIN + path
    og_img = DOMAIN + "/assets/share-logo.png"
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:locale" content="zh_CN">
<meta property="og:site_name" content="冯氏族谱">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{og_url}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="512">
<meta property="og:image:height" content="512">
<meta property="og:image:alt" content="冯氏族谱「冯」字标志">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_img}">
<link rel="icon" href="/icon.svg">
<link rel="stylesheet" href="/assets/style.css?v=shared-theme-1">
{extra_css}<link rel="stylesheet" href="/assets/genealogy-theme.css?v={THEME_V}">
</head>
<body class="site-theme">
"""


def header(active="archives"):
    on_home = ' class="on" aria-current="page"' if active == "home" else ""
    on_arch = ' class="on" aria-current="page"' if active == "archives" else ""
    return f"""<header class="site-header"><a class="brand" href="/"><img src="/icon.svg" alt="" width="46" height="46"><span>冯氏族谱<small>fengshizupu.com</small></span></a></header>
<nav class="mainnav" aria-label="主导航"><div class="mainnav-in"><a href="{MAIN}/"{on_home}>首页</a><a href="{MAIN}/news/">资讯</a><a href="{MAIN}/archives/"{on_arch}>族谱</a><a href="{MAIN}/about/">关于</a><span class="share-wrap"><button type="button" class="share-text" onclick="sharePage()">分享</button></span></div></nav>
"""


# 主站主页搜索框下方的栏目（2026-11-16 自 fengshizupu.com 主页原样复制，站内链接改为绝对地址；
# 主站日后更新这些栏目时，这里要跟着同步一次）
MAIN_SECTIONS = """
<section class="home-news"><div class="home-news-head"><h2>冯氏资讯</h2><a href="https://fengshizupu.com/news/">全部资讯 ›</a></div>
<p class="home-news-item"><span class="badge">人物</span> <a href="https://fengshizupu.com/news/enping/feng-ru-enping-aviation/">从恩平杏圃村到美国奥克兰：冯如的航空生涯</a> <small>2026 年 11 月 15 日</small></p>
<p class="home-news-item"><span class="badge">指南</span> <a href="https://fengshizupu.com/news/enping/enping-feng-juanshou-guide/">第一次翻《恩平冯氏族谱》卷首，先看哪几页？</a> <small>2026 年 11 月 15 日</small></p></section>
<a class="enping-card" href="https://enping.fengshizupu.com" target="_blank" rel="noopener noreferrer"><span class="enping-seal">冯</span><span class="enping-body"><span class="enping-title">《恩平冯氏族谱》全书在线查阅</span><span class="enping-motto">寻根溯源 · 世系传承</span><span class="enping-intro">恩平冯氏总谱全书 1,269 页逐页看图，可按房支、村庄查找<span class="enping-more">　去看全书 ›</span></span></span><span class="enping-btn">看全书</span></a>
<article><h2>各地族谱</h2><p>从各地族谱入口查阅原书、续修谱和世系资料。</p><a href="https://fengshizupu.com/archives/">进入族谱目录 →</a></article>
<section><h2>冯氏宗亲网站</h2><ul>
<li><a href="http://www.feng0762.com/" target="_blank" rel="noopener noreferrer">冯氏宗亲网</a> — 冯氏宗亲论坛，各地宗亲会与寻根交流</li>
<li><a href="https://www.lulugu.com/feng" target="_blank" rel="noopener noreferrer">中华家谱网 · 冯氏族谱</a> — 各地冯氏家谱条目与谱书预览</li>
<li><a href="https://www.jiapu.tv/x/54/" target="_blank" rel="noopener noreferrer">中国家谱网 · 冯氏家谱</a> — 按《中国家谱总目》著录的冯氏家谱目录</li>
<li><a href="http://jp5000.com/fengb" target="_blank" rel="noopener noreferrer">百姓通谱网 · 冯氏家谱网</a> — 冯氏宗祠、字辈与姓氏文化</li>
<li><a href="https://wiki.zupulu.com/doc.php?action=view&amp;docid=1621" target="_blank" rel="noopener noreferrer">族谱录 · 冯姓</a> — 冯姓起源、郡望与堂号</li>
<li><a href="https://www.library.sh.cn/special/GenealogyLibrary/" target="_blank" rel="noopener noreferrer">上海图书馆家谱馆</a> — 家谱馆藏检索与寻根服务</li>
<li><a href="https://www.mychinaroots.com/surnames/detail?word=%E5%86%AF" target="_blank" rel="noopener noreferrer">My China Roots · 冯</a> — 英文寻根平台的冯姓页（海外宗亲）</li>
</ul></section>
<a class="enping-card" href="https://fengshizupu.com/enping-fengshi-juanshou/"><span class="enping-seal">冯</span><span class="enping-body"><span class="enping-title">《恩平冯氏族谱 · 卷首影印》</span><span class="enping-motto">始平世泽 · 大树家声</span><span class="enping-intro">恩平冯氏总谱卷首影印：谱序、倡修经过与修谱合影<span class="enping-more">　在线阅览 ›</span></span></span><span class="enping-btn">在线阅览</span></a>
"""


def footer():
    return f"""<footer class="site-footer">冯氏族谱 · 留存原谱，连接宗亲<br>
全国数字族谱平台 · <a href="{MAIN}/">fengshizupu.com</a> · <a href="{MAIN}/about/">关于本站</a></footer>
</body>
</html>
"""


def book_total_pages(book):
    return sum(v["pages"] for v in book["volumes"])


def index_page(books):
    # 首页照抄主站主页：结构与样式与 fengshizupu.com 主页一致（样式 = assets/main-home.css，
    # 即主站主页同款样式文件的快照；主站改版后需同步更新）。差别只有两处：
    # ① 搜索搜本站收录的谱书；② 搜索下方每部谱一张卡片（与主站恩平卡同款式）。
    cards = ""
    for b in books:
        q = f'{b["title"]} {b["keywords"]}'
        intro = f'{b["place"]} · {len(b["volumes"])} 册 · {book_total_pages(b)} 页，逐页在线连读'
        cards += (f'<a class="enping-card" href="/book/{b["slug"]}.html" data-q="{q}">'
                  f'<span class="enping-seal">冯</span><span class="enping-body">'
                  f'<span class="enping-title">《{b["title"]}》</span>'
                  f'<span class="enping-motto">{b["era"]}</span>'
                  f'<span class="enping-intro">{intro}<span class="enping-more">　在线阅读 ›</span></span></span>'
                  f'<span class="enping-btn">看全书</span></a>\n')
    sections = f'<div class="book-cards">\n{cards}</div>\n'
    total_books = len(books)
    total_pages = sum(book_total_pages(b) for b in books)
    return head("各地冯氏族谱收藏 · 冯氏族谱",
                "各地冯氏族谱收藏：收录图书馆藏本冯氏宗谱影印，逐页在线连读。",
                '<link rel="stylesheet" href="/assets/main-home.css?v=20261116">\n') + header("home") + f"""<main>
<section class="hero"><p class="eyebrow">全国冯氏宗亲 · 数字族谱档案</p>
<h1>寻根有据，世系有源。</h1>
<p>从一页家谱，读懂一家人的来处。留存珍贵原谱，让宗亲记忆代代相传。</p>
<div class="regional-search"><form class="hero-search" onsubmit="return false"><input id="bookSearch" type="text" placeholder="输入地名或书名，如：乐清、湘潭、宗谱" aria-label="搜索本站收录的谱书"><button type="submit">搜索</button></form><small>输入地名或书名，筛选本站收录的谱书（目前收录 {total_books} 部、{total_pages} 页，陆续增补）。</small></div>
<p class="note" id="bookStatus"></p>
</section>
{sections}""" + MAIN_SECTIONS + f"""
</main>
{FAB}
<script src="/assets/site.js?v=2"></script>
<script>filterList('bookSearch', 'bookStatus', '.book-cards .enping-card', '部');</script>
""" + FAB_SCRIPT + footer()


DL_BASE = "https://github.com/alititi-jackie/fengshizupu-zp2/releases/download/b-20261116"


def book_page(b):
    rows = ""
    for v in b["volumes"]:
        rows += (f'<a href="/read/{b["slug"]}-{v["id"]}.html"><span>{v["name"]}</span>'
                 f'<span class="pg">{v["pages"]} 页 · 打开阅读 ›</span></a>\n')
    desc = f'{b["title"]}：{b["era"]}，{b["editors"]}。{b["source"]}，全 {len(b["volumes"])} 册 {book_total_pages(b)} 页，在线连读。'
    return head(f'{b["title"]} · 冯氏族谱', desc, path=f'/book/{b["slug"]}.html') + header() + f"""<main>
<p class="crumb"><a href="/">族谱收藏</a> / {b["province"]} · {b["place"]}</p>
<h1>{b["title"]}</h1>
<div class="kv">
<p><strong>纂修年代：</strong>{b["era"]}</p>
<p><strong>纂辑者：</strong>{b["editors"]}</p>
<p><strong>藏本来源：</strong>{b["source"]}</p>
<p><strong>全书规模：</strong>{len(b["volumes"])} 册，共 {book_total_pages(b)} 页</p>
</div>
<p>{b["intro"]}</p>
<section class="block"><h2>各册阅读</h2>
<div class="list">
{rows}</div></section>
<p class="note">阅读说明：点开任意一册即从第一页连续向下阅读，可跳页、可点图放大；每册阅读页顶部可下载 PDF 版。</p>
</main>
{FAB}
""" + FAB_SCRIPT + footer()


def dl_row(b, v):
    if not v.get("dl_mb"):
        return ""
    return (f'<div class="dlrow"><a href="{DL_BASE}/{b["slug"]}-{v["id"]}-dl.pdf">'
            f'下载本册 PDF · {v["dl_mb"]} MB</a></div>\n')


def reader_page(b, v):
    title = f'{b["title"]}（{v["name"]}）'
    pages = [None] + [{"label": f"第 {i} 页"} for i in range(1, v["pages"] + 1)]
    numeric = {str(i): i for i in range(1, v["pages"] + 1)}
    data = {"title": title, "base": f'/img/{b["slug"]}/{v["id"]}/',
            "pages": pages, "numeric": numeric, "start": 1}
    data_json = json.dumps(data, ensure_ascii=False)
    return head(f'{title} · 在线连读 · 冯氏族谱',
                f'{title}在线连读：{b["era"]}，{b["source"]}。',
                path=f'/read/{b["slug"]}-{v["id"]}.html') + header() + f"""<div class="wrap">
<div class="readerbar">
<a class="nav" href="/book/{b["slug"]}.html">返回目录</a>
<span class="info" id="info" aria-live="polite"></span>
<span class="info" id="branchInfo"></span>
<span class="reader-spacer"></span>
<span class="modes"><button id="mSingle" type="button">单页</button><button id="mScroll" type="button">连看</button></span>
<button id="jumpToggle" type="button">跳页</button>
<label class="info jumpctl">页码 <input id="jump" type="number" min="1" max="{v['pages']}"></label>
<button class="primary" id="jumpBtn">跳页</button>
</div>
{dl_row(b, v)}<div class="readerwrap">
<button id="singlePage" class="reader-image" type="button" aria-label="放大当前谱页"><img class="pageimg" id="pg" alt="族谱原书页"></button>
<div id="scrollView" style="display:none"></div>
<div class="pagenav"><a id="prev" href="#">← 上一页</a><a id="next" href="#">下一页 →</a></div>
</div>
</div>
<dialog id="imageDialog" class="image-dialog" aria-labelledby="imageLabel">
<div class="image-toolbar"><span id="imageLabel"></span><button type="button" id="imageZoom">放大查看</button><button type="button" id="imageClose">关闭</button></div>
<div class="image-viewport"><img id="imageLarge" alt=""></div>
</dialog>
{FAB}
<script src="/assets/site.js?v=2"></script>
<script id="originalReaderData" type="application/json">{data_json}</script>
<script src="/assets/reader-controls.js?v=1" defer></script>
<script src="/assets/volume-reader.js?v=1" defer></script>
""" + FAB_SCRIPT + footer()


def main():
    data = json.load(open(os.path.join(ROOT, "data", "books.json"), encoding="utf-8"))
    books = data["books"]
    if os.path.exists(OUT):
        # keep rendered images if present (img/ is produced by render_pages.py)
        img_dir = os.path.join(OUT, "img")
        saved = None
        if os.path.exists(img_dir):
            saved = os.path.join(ROOT, ".img-keep")
            if os.path.exists(saved):
                shutil.rmtree(saved)
            shutil.move(img_dir, saved)
        shutil.rmtree(OUT)
        os.makedirs(OUT)
        if saved:
            shutil.move(saved, img_dir)
    else:
        os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"))
    icon = open(os.path.join(ROOT, "assets", "icon.svg"), encoding="utf-8").read()
    for name in ("icon.svg", "favicon.svg"):
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(icon)
    open(os.path.join(OUT, "CNAME"), "w").write("zp2.fengshizupu.com\n")

    urls = [f"{DOMAIN}/"]
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(index_page(books))
    os.makedirs(os.path.join(OUT, "book"))
    os.makedirs(os.path.join(OUT, "read"))
    for b in books:
        open(os.path.join(OUT, "book", b["slug"] + ".html"), "w", encoding="utf-8").write(book_page(b))
        urls.append(f'{DOMAIN}/book/{b["slug"]}.html')
        for v in b["volumes"]:
            name = f'{b["slug"]}-{v["id"]}.html'
            open(os.path.join(OUT, "read", name), "w", encoding="utf-8").write(reader_page(b, v))
            urls.append(f"{DOMAIN}/read/{name}")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"<url><loc>{u}</loc></url>" for u in urls]
    sm.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm))
    open(os.path.join(OUT, "robots.txt"), "w").write(
        f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    print(f"generated {len(urls)} pages into site/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
