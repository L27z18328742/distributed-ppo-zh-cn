#!/usr/bin/env python3
"""从用户提供的 HTML 和逐段译文重建纯静态中文阅读站。"""
from pathlib import Path
import copy
import html
import json
from bs4 import BeautifulSoup, NavigableString, Comment

ROOT = Path(__file__).resolve().parent
WEB = ROOT / 'webapp'
SOURCE_URL = 'https://makinarocks.github.io/Distributed-PPO-implementation/'
DESCRIPTIONS = [
    '强化学习项目中的训练时间瓶颈。',
    'PPO、TRPO 与裁剪目标，以及进一步阅读的资料。',
    'N 个 Actor、T 个时间步、M 大小的小批量与 K 轮训练。',
    'Learner 与 Actor 的职责，以及 PPO 的四个功能模块。',
    '远程对象、远程方法调用和异步结果引用。',
    '同步模型、并行采样、汇总轨迹、训练与再次同步。',
    '原文实验：8 个 Actor 与单个 Actor 的奖励曲线。',
    '轨迹收集的分布式处理与模型训练的进一步扩展。',
]

def fragment(value):
    return BeautifulSoup(value, 'html.parser')

def translate():
    source = BeautifulSoup((ROOT / 'src/original.html').read_text(), 'html.parser').select_one('.article-post')
    article = copy.deepcopy(source)
    nodes = [x for x in article.descendants if isinstance(x, NavigableString)
             and not isinstance(x, Comment) and x.strip() and x.parent.name not in ('code', 'pre')]
    translations = json.loads((ROOT / 'src/translations.json').read_text())
    assert len(nodes) == len(translations), (len(nodes), len(translations))
    for node, translation in zip(nodes, translations):
        node.replace_with(translation)
    for node in article.find_all(string=lambda x: isinstance(x, Comment)):
        node.extract()
    for node in article.select('div[style]'):
        node.decompose()
    for block in article.select('pre code'):
        text = block.get_text().replace('# remote class (ray actor) 생성', '# 创建远程类实例（Ray Actor）').replace('# remote method call', '# 远程方法调用')
        block.string = text
    captions = [
        '图 1 · PPO 的 Actor-Critic 形式伪代码。N 个 Actor 分别收集 T 个时间步的数据；用大小为 M ≤ NT 的小批量优化 K 轮，然后更新旧策略参数。',
        '图 2 · PPO 的模块关系。Model：模型；Agent：智能体；Sampler：采样器；Trainer：训练器；Env：环境；Optimizer：优化器。Agent 包含 Model，Sampler 组合 Agent 与环境，Trainer 组合 Agent 与优化器。',
        '图 3 · 8 个 Actor 与单个 Actor 的训练曲线。横轴为时间，纵轴为回合奖励；蓝色为单 Actor，其余曲线为分布式 Actor。原图未注明时间单位。',
    ]
    for im, caption in zip(article.select('img'), captions):
        im['src'] = 'assets/images/' + Path(im['src']).name
        im['alt'] = caption
        figure = fragment('<figure></figure>').figure
        im.parent.replace_with(figure)
        figure.append(im)
        figcaption = fragment('<figcaption></figcaption>').figcaption
        figcaption.string = caption
        figure.append(figcaption)
    # 原图保留，图内算法额外提供完整中文文字版。
    article.select('figure')[0].insert_after(fragment('''<details class="figure-text"><summary>图 1 的中文文字版</summary>
<p><strong>算法 1：PPO（Actor-Critic 形式）</strong></p>
<ol><li>对每次迭代（iteration = 1, 2, …）：<ol><li>对每个 Actor（actor = 1, 2, …, N）：在环境中运行旧策略 π<sub>θ_old</sub> 共 T 个时间步，计算优势估计 Â₁, …, Â<sub>T</sub>。</li><li>针对参数 θ 优化代理目标 L；共进行 K 轮训练，小批量大小为 M ≤ NT。</li><li>更新旧策略参数：θ<sub>old</sub> ← θ。</li></ol></li></ol></details>'''))
    notes = {
        2: '“理论上加快 N 倍”描述的是理想条件下的采样阶段。实际加速还受环境负载、通信与同步开销影响，不等于整个训练过程加快 N 倍。',
        4: '原文使用 Future 一词；Ray 文档使用 ObjectRef 表示异步结果引用。原例的 <code>ray.wait(future)</code> 保留原样；API 要求传入引用列表，应写作 <code>ray.wait([future])</code>。此外，<code>ray.init()</code> 可初始化本地实例，也可连接集群。见 <a href="https://docs.ray.io/en/latest/ray-core/api/doc/ray.wait.html">ray.wait 文档</a>与 <a href="https://docs.ray.io/en/latest/ray-core/api/doc/ray.init.html">ray.init 文档</a>。',
        5: '这段代码是结构示意。原文 <code>set_model</code> 定义缺少冒号，且混用了制表符和空格；<code>PPOActorRemote()</code> 按 Ray 的 Actor 创建方式应为 <code>PPOActorRemote.remote()</code>。译文保留原代码，仅翻译注释；不可直接当作完整训练脚本运行。见 <a href="https://docs.ray.io/en/latest/ray-core/actors.html">Ray Actor 文档</a>。',
        6: '这是作者在 2020 年文章中展示的实验结果。原文未给出完整环境、硬件配置、时间单位或可复现实验脚本；此图不构成普遍的加速比保证。',
    }
    sections = []
    for i, heading in enumerate(article.select('h2')):
        heading['id'] = f'ch{i + 1:02d}'
        parts = [str(heading)]
        sibling = heading.next_sibling
        while sibling is not None and getattr(sibling, 'name', None) != 'h2':
            parts.append(str(sibling))
            sibling = sibling.next_sibling
        if i in notes:
            parts.append('<aside class="translator-note"><strong>译者注</strong><p>' + notes[i] + '</p></aside>')
        sections.append((heading.get_text(), ''.join(parts)))
    (ROOT / 'content/article.html').write_text('<h1>分布式 PPO 的实现</h1>\n' + '\n'.join(body for _, body in sections))
    return source, sections

def page(title, body, toc, prefix='', pager=''):
    return f'''<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — 分布式 PPO 中文版</title>
<meta name="description" content="MakinaRocks 技术文章《Distributed PPO 구현》的简体中文译本：PPO 采样流程、Learner 与 Actor、Ray 远程对象及分布式实现。">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/style.css"><link rel="stylesheet" href="{prefix}assets/site.css"></head>
<body><header class="topbar"><a class="brand" href="{prefix}index.html">分布式 PPO 中文版<span>MakinaRocks 技术博客</span></a>
<nav class="chapnav" aria-label="阅读导航"><a href="{prefix}index.html">目录</a><a href="{prefix}full.html">全文阅读</a><a href="{SOURCE_URL}">原文 ↗</a></nav></header>
<div class="layout"><aside class="sidebar"><nav class="toc" aria-label="章节目录"><h2>阅读目录</h2><ol>{toc}</ol></nav></aside>
<main class="main"><details class="mobile-toc"><summary>阅读目录</summary><ol>{toc}</ol></details>
<article class="prose">{body}</article>{pager}
<footer class="pagefoot">非官方中文译本 · 原作者 jemin kim（MakinaRocks） · 原文发表于 2020-12-01 · <a href="{SOURCE_URL}">原文链接</a>。依据用户提供的本地 HTML 翻译；正文、插图与代码的权利归原权利人所有。译者注与原文分开标示。</footer></main></div>
<script src="{prefix}assets/site.js"></script></body></html>'''

def main():
    source, sections = translate()
    (WEB / 'chapters').mkdir(exist_ok=True)
    cards = []
    for i, (title, _) in enumerate(sections):
        cards.append(f'<a class="card" href="chapters/ch{i+1:02d}.html"><span class="no">第 {i+1} 节</span><span class="zh">{html.escape(title)}</span><span class="desc">{DESCRIPTIONS[i]}</span></a>')
    toc = ''.join(f'<li><a href="chapters/ch{i+1:02d}.html">{i+1:02d}　{html.escape(t)}</a></li>' for i,(t,_) in enumerate(sections))
    intro = '''<div class="reading-head"><div class="eyebrow">简体中文译本 · 技术文章</div><h1>分布式 PPO 的实现</h1><p class="subtitle">Distributed PPO 구현</p><p>原作者：jemin kim · MakinaRocks · 2020 年 12 月 1 日</p><p>通过 Ray 并行收集轨迹，缩短 PPO 的训练时间。从训练流程和模块职责讲起，逐步介绍远程对象、异步结果与分布式采样的实现。</p><div class="reading-meta"><span>8 个章节</span><span>3 张原图</span><span>10 个代码块</span></div><a class="read-button" href="chapters/ch01.html">开始阅读 →</a><a class="full-link" href="full.html">全文阅读</a></div><h2>章节目录</h2>'''
    (WEB / 'index.html').write_text(page('目录', intro + '<div class="chapter-grid">'+''.join(cards)+'</div>', toc))
    full_toc = ''.join(f'<li><a href="#ch{i+1:02d}">{i+1:02d}　{html.escape(t)}</a></li>' for i,(t,_) in enumerate(sections))
    (WEB / 'full.html').write_text(page('全文阅读', '<h1>分布式 PPO 的实现</h1><p class="article-meta">jemin kim · MakinaRocks · 2020-12-01</p>' + ''.join(b for _,b in sections), full_toc))
    for i,(title,body) in enumerate(sections):
        chapter_toc = toc.replace('href="chapters/', 'href="')
        chapter_toc = chapter_toc.replace(f'href="ch{i+1:02d}.html"',f'class="active" aria-current="page" href="ch{i+1:02d}.html"')
        previous = f'<a href="ch{i:02d}.html"><span class="dir">← 上一节</span><div class="ttl">{html.escape(sections[i-1][0])}</div></a>' if i else '<a href="../index.html">← 文章目录</a>'
        following = f'<a class="next" href="ch{i+2:02d}.html"><span class="dir">下一节 →</span><div class="ttl">{html.escape(sections[i+1][0])}</div></a>' if i < len(sections)-1 else '<a class="next" href="../full.html">全文阅读 →</a>'
        body = body.replace('<h2 ', '<h1 ', 1).replace('</h2>', '</h1>', 1).replace('src="assets/', 'src="../assets/')
        (WEB / f'chapters/ch{i+1:02d}.html').write_text(page(title, f'<p class="article-meta">第 {i+1} 节 / 共 8 节</p>'+body, chapter_toc,'../','<nav class="pager" aria-label="章节翻页">'+previous+following+'</nav>'))
    print(f'已构建：1 个目录页、1 个全文页、{len(sections)} 个章节页。')

if __name__ == '__main__':
    main()
