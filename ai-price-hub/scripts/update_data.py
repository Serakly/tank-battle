#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ai-price-hub 每日数据更新。

- 汇率：open.er-api.com（免费、无需 Key），每次运行必更新
- API 价格：尽力抓取官方文档页（OpenAI / Anthropic / 智谱），
  抓取或解析失败时保留旧值，并在 scrape_status 里标记原因
- 订阅价格：厂商改价频率低，直接人工维护 data/prices.json
  （自动抓取只更新 api_prices 里带 "auto" 字段的行）

用法:
    python update_data.py            # 更新并写回 data/prices.json
    python update_data.py --dry-run  # 只打印结果，不写文件
"""
import argparse
import datetime
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "prices.json"
CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CNY", "INR"]
UA = {"User-Agent": "Mozilla/5.0 (compatible; ai-price-hub-updater/1.0)"}

PAGES = {
    "openai": "https://developers.openai.com/api/docs/pricing",
    "anthropic": "https://platform.claude.com/docs/en/docs/about-claude/models",
    "bigmodel": "https://docs.bigmodel.cn/cn/guide/start/pricing",
}


def fetch(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def strip_tags(s: str) -> str:
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    return html.unescape(re.sub(r"<[^>]+>", " ", s))


def update_fx(data: dict, status: dict) -> None:
    try:
        j = json.loads(fetch("https://open.er-api.com/v6/latest/USD"))
        rates = j["rates"]
        data["fx"] = {
            "base": "USD",
            "rates": {c: rates[c] for c in CURRENCIES},
            "as_of": j.get("time_last_update_utc", ""),
        }
        status["fx"] = "ok"
    except Exception as e:  # noqa: BLE001
        status["fx"] = f"kept ({e})"


def parse_openai(text: str, model: str, _extra=None):
    """developers.openai.com/api/docs/pricing 的行结构（展平后）：
    模型id  $in  $cached_in  $cache_write  $out  $in*2 ... （Fast mode 等）。
    取前 4 个数字作为标准档。"""
    m = re.search(re.escape(model) + r"(?![\w.-])", text)
    if not m:
        return None
    nums = re.findall(r"\$\s*(\d+(?:\.\d+)?)", text[m.end(): m.end() + 300])
    if len(nums) < 4:
        return None
    inp, cached, _write, out = (float(x) for x in nums[:4])
    return inp, out, cached


def parse_anthropic(text: str, model: str, page_map=None):
    """platform.claude.com 模型页：价格卡 "$N / input MTok $M / output MTok"
    与 "Claude API ID" 后的 id 列表按顺序一一对应。"""
    if page_map is None:
        pairs = re.findall(
            r"\$(\d+(?:\.\d+)?)\s*/\s*input\s*MTok\s*\$(\d+(?:\.\d+)?)\s*/\s*output\s*MTok",
            text,
        )
        ids = []
        for mid in re.findall(r"claude-[a-z0-9][\w.-]+", text):
            if mid not in ids:
                ids.append(mid)
        if len(pairs) != len(ids) or not pairs:
            return None
        page_map = dict(zip(ids, pairs))
    hit = page_map.get(model)
    if hit is None:  # id 带日期后缀等，做前缀匹配
        cands = [v for k, v in page_map.items() if k.startswith(model)]
        hit = cands[0] if cands else None
    if hit is None:
        return None
    inp, out = float(hit[0]), float(hit[1])
    return inp, out, None


def parse_bigmodel(text: str, model: str, _extra=None):
    """docs.bigmodel.cn 定价页表格（展平后）：
    模型名 [上下文/分档说明] 输入 输出 限时免费 缓存命中 ..."""
    m = re.search(re.escape(model) + r"(?![\w.-])", text, re.I)
    if not m:
        return None
    seg = text[m.end(): m.end() + 220]
    p = re.search(
        r"(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s*限时免费\s*(\d+(?:\.\d+)?)", seg
    )
    if not p:
        return None
    inp, out, cache = float(p.group(1)), float(p.group(2)), float(p.group(3))
    return inp, out, cache


PARSERS = {"openai": parse_openai, "anthropic": parse_anthropic, "bigmodel": parse_bigmodel}


def update_api_prices(data: dict, status: dict) -> None:
    pages = {}
    for key, url in PAGES.items():
        try:
            pages[key] = strip_tags(fetch(url))
        except Exception as e:  # noqa: BLE001
            status.setdefault(key, f"fetch failed ({e})")

    page_map_cache = {}
    for row in data.get("api_prices", []):
        auto = row.get("auto")
        if not auto or auto not in pages:
            continue
        try:
            found = PARSERS[auto](pages[auto], row["model"], page_map_cache.get(auto))
        except Exception as e:  # noqa: BLE001
            status[auto] = f"parse failed ({e})"
            continue
        if found:
            inp, out, cache = found
            row["input"], row["output"] = inp, out
            if cache is not None:
                row["cache_read"] = cache
            elif row.get("cache_read_pct"):
                row["cache_read"] = round(inp * row["cache_read_pct"] / 100, 4)
            row["as_of"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
            status[auto] = "ok"
        else:
            status.setdefault(auto, "kept (model/price not found)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="只打印，不写回")
    args = ap.parse_args()

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    status: dict = {}
    update_fx(data, status)
    update_api_prices(data, status)
    data["updated_at"] = (
        datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds") + "Z"
    )
    data["scrape_status"] = status

    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if args.dry_run:
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return
    DATA_FILE.write_text(out, encoding="utf-8")
    print(json.dumps(status, ensure_ascii=False))
    for k, v in status.items():
        if v != "ok":
            print(f"note: {k}: {v}", file=sys.stderr)


if __name__ == "__main__":
    main()
