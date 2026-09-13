# 坦克大战 (Battle City)

一个纯 HTML5 / Canvas 实现的经典《坦克大战》复刻版。单个 `index.html` 文件,无需任何依赖,浏览器直接打开即可游玩。

## 试玩

- 直接双击打开 `index.html`,或部署到任意静态站点(GitHub Pages 等)。
- 在线试玩:https://serakly.github.io/tank-battle/

## 玩法

| 操作 | 按键 |
| --- | --- |
| 移动 | `WASD` 或 方向键 |
| 开火 | `空格` 或 `J` |
| 暂停 / 继续 | `P` 或 `Esc` |
| 静音 | `M` |
| 开始 / 重开 / 下一关 | `Enter` |

- 保护底部基地的**鹰旗**,被击毁则游戏结束。
- 消灭所有敌人即可过关,进入下一关。
- 击毁带标记的敌人会掉落道具:⭐升级、✸全屏击杀、⛨护盾、♜加命、♠修复基地围墙。

## 特性

- 经典 13×13 砖墙 / 钢墙 / 河流 / 草丛地图
- 玩家坦克 + 敌方 AI(多种类型:普通 / 快速 / 装甲 / 强化)
- 可破坏的砖墙、不可破坏的钢墙、可藏身的草丛
- 道具系统、计分、生命、无限关卡递增难度
- Web Audio 音效(可静音)
- 移动端触屏方向键 + 开火按钮

## 运行

无需构建,直接打开 `index.html` 即可:

```bash
# 或启动一个本地静态服务器
python -m http.server 8000
# 浏览器访问 http://localhost:8000
```

## 文件结构

```
.
├── index.html   # 游戏全部代码(HTML + CSS + JS 单文件)
└── README.md
```

## 其他项目

- [AI 价格雷达](ai-price-hub/) —— OpenAI/Codex、Claude、智谱 GLM、豆包等 AI 的各国订阅价 & API 单价，每日自动更新。
  在线访问: <https://serakly.github.io/tank-battle/ai-price-hub/>
