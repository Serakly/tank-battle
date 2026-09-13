# AI 价格雷达 · ai-price-hub

一个纯静态网站，展示热门 AI 服务（OpenAI / Codex、Anthropic / Claude、智谱 GLM、字节豆包等）的：

- **订阅价格** —— 按国家/地区列出售价（美国、欧元区、英国、日本、印度、中国），支持折算成任意主要货币
- **API 价格** —— 旗舰模型每百万 tokens 的输入 / 输出 / 缓存单价

数据每天自动更新（汇率必更新；官方页可抓取的 API 价格自动刷新），页面顶部显示数据时间。

## 本地运行

```bash
cd ai-price-hub
python -m http.server 8000
# 浏览器打开 http://localhost:8000
```

> 页面通过 `fetch` 读取 `data/prices.json`，直接双击 `index.html`（file://）在部分浏览器里会被 CORS 拦截，请用本地服务器或 GitHub Pages 访问。

## 目录结构

```
ai-price-hub/
├── index.html              # 站点本体（单文件，无依赖）
├── data/prices.json        # 全部价格数据（含来源与更新时间）
├── scripts/update_data.py  # 每日更新脚本
└── README.md
```

## 每日更新机制

仓库根的 `.github/workflows/update-ai-prices.yml` 每天北京时间 00:30 运行：

1. 拉取最新汇率（[open.er-api.com](https://open.er-api.com)，免费无需 Key）
2. 尽力抓取官方文档页上的 API 价格（OpenAI、Anthropic、智谱），失败则保留旧值并在 `scrape_status` 标注
3. 有变化就自动 commit + push；GitHub Pages 随之重新部署

手动触发：Actions 页 → "每日更新 AI 价格数据" → Run workflow。
本地触发：`python scripts/update_data.py`（`--dry-run` 只看结果）。

## 如何维护订阅价格

订阅价厂商改得很慢，直接编辑 `data/prices.json` 的 `subscriptions` 数组即可：

- 每条含 `countries`（按 `US/EU/UK/JP/IN/CN` 六国），值为 `{amount, currency, tax?, note?, approx?}` 或 `null`（表示该地区不销售 / 以美元计价）
- `approx: true` 会在页面上显示"约"标记
- 改完提交即可，脚本不会覆盖订阅区数据

## 数据来源

- OpenAI：[chatgpt.com/pricing](https://chatgpt.com/pricing/)、[Codex 定价](https://chatgpt.com/codex/pricing/)、[API 定价](https://developers.openai.com/api/docs/pricing)
- Anthropic：[anthropic.com/pricing](https://www.anthropic.com/pricing)、[模型与价格文档](https://platform.claude.com/docs/en/docs/about-claude/models)
- 智谱：[bigmodel.cn/glm-coding](https://bigmodel.cn/glm-coding)、[API 定价文档](https://docs.bigmodel.cn/cn/guide/start/pricing)、[z.ai/subscribe](https://z.ai/subscribe)
- 豆包：[火山方舟模型价格](https://www.volcengine.com/docs/82379/1544106)
- 汇率：[open.er-api.com](https://open.er-api.com/v6/latest/USD)

> ⚠️ 各家价格（尤其促销价、分档价、税费）变动频繁，本站数据仅供参考，下单前请以官方页面为准。
