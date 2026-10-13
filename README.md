# 分布式 PPO 的实现 — 简体中文阅读站

原作者：jemin kim，MakinaRocks。原文发表于 2020-12-01。

原文：https://makinarocks.github.io/Distributed-PPO-implementation/

本文依据用户提供的本地 HTML 完整翻译文章正文，保留 8 个章节、3 张原图、10 个代码块和原文参考链接。米色背景、紫色强调色、侧栏目录及章节卡片参考本地 `ultrascale-playbook-zh-tw` 阅读站。提供目录页、章节页和全文页；静态页面无外部运行时依赖，正文无需 JavaScript 即可阅读。

```bash
cd /Users/lezewei/project/study/blog/distributed-ppo-zh-cn
bash run.sh
```

访问 http://127.0.0.1:8650/ 。如需更换端口：`bash run.sh 8651`。

## 文件

- `src/original.html`：用户提供的原文快照，保留用于对照；不加载原站追踪或评论脚本。
- `src/source.json`：作者、发布日期、来源和快照 SHA-256。
- `src/translations.json`：按原文正文文本节点排序的完整译稿。
- `content/article.html`：生成的完整中文正文。
- `webapp/`：可直接打开的静态站点与本地图片。
- `build.py`：重建命令 `python3 build.py`，需要 Beautiful Soup 4（见 requirements.txt）。

## 翻译约定

简体中文；PPO、TRPO、Ray、Actor、Learner 和代码标识符保留英文。代码仅翻译注释，其他代码内容保持原样。原图保留，配中文图注；算法图另附完整中文文字版，模块图图注逐项翻译图中文字。

原文示例是 2020 年的伪代码，并非完整可运行的 PPO 工程。`ray.wait(future)` 的引用列表问题、远程 Actor 的 `.remote()` 创建方式，以及缺失冒号、混合缩进等问题另列译者注。原文关于 T 小于回合长度的表述保留；这是文中的设置说明。性能图来自作者当时的实验，没有注明时间单位，也没有提供完整复现配置。

翻译覆盖文章正文，不包含原网站的评论服务、其他文章推荐和全站导航。原文、图片及代码权利归原权利人所有；本地译本未另行赋予原文开放许可。
