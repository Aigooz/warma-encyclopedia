# Warma 百科

B站UP主 [Warma](https://space.bilibili.com/53456)（主号）与 [warma养鸽场](https://space.bilibili.com/106320250)（小号）的数据百科与可视化项目。

## 项目结构

```
├── site/                    # 可视化网站（打开 index.html）
│   ├── index.html           # 主页面
│   ├── app.js               # 图表逻辑
│   ├── data.js              # 全量数据（359个视频）
│   └── style.css            # 样式
├── tools/                   # 自动化工具
│   ├── update.py            # 全自动更新入口
│   ├── build_site_data.py   # 生成 site/data.js
│   ├── enrich_xlsx_insights.py  # 表格增强
│   ├── fetch_danmaku.py     # 弹幕抓取
│   └── ...
├── charts/                  # 静态图表
├── subtitles/               # 字幕 JSON
├── registry.json            # 视频注册表
├── config.ini               # 配置（Cookie 等，不入库）
├── 一键更新百科.bat          # 交互式更新
├── 一键更新表格.bat          # Excel 更新
├── 同步到GitHub.bat          # 手动同步
└── 使用说明.md
```

## 使用

1. **一键更新**：双击 `一键更新百科.bat` 选择模式
2. **更新表格**：双击 `一键更新表格.bat`
3. **同步 GitHub**：更新脚本会自动推送，或双击 `同步到GitHub.bat`

## 网站预览

用浏览器打开 `site/index.html` 即可，无需服务器。

包含：年度趋势、类型分布、时长热力图、弹幕峰值、标题关键词网络、发布时段时钟、封面画廊等 20+ 可视化模块。