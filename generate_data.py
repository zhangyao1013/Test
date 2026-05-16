#!/usr/bin/env python3
"""生成 data.csv 测试数据，供 data_plot.py 等脚本使用。"""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# 与 index.html 问题列表一致的基础样本
BASE_ISSUES = [
    {
        "id": 1,
        "description": "张三：电动车违停导致通行受阻",
        "assignee": "张三",
        "type": "功能问题",
        "created": "2026-05-16 09:00",
        "status": "延期修复",
        "priority_score": 8,
        "resolve_hours": 36,
    },
    {
        "id": 2,
        "description": "李四：登录按钮颜色与风格不一致",
        "assignee": "李四",
        "type": "体验问题",
        "created": "2026-05-16 10:30",
        "status": "正常",
        "priority_score": 4,
        "resolve_hours": 12,
    },
    {
        "id": 3,
        "description": "王五：表单验证未提示必要字段",
        "assignee": "王五",
        "type": "功能问题",
        "created": "2026-05-16 11:20",
        "status": "延期修复",
        "priority_score": 7,
        "resolve_hours": 48,
    },
    {
        "id": 4,
        "description": "赵六：页面滚动时卡顿体验差",
        "assignee": "赵六",
        "type": "体验问题",
        "created": "2026-05-16 12:05",
        "status": "正常",
        "priority_score": 5,
        "resolve_hours": 18,
    },
]

ASSIGNEES = ["张三", "李四", "王五", "赵六", "钱七", "孙八"]
TYPES = ["功能问题", "体验问题", "性能问题"]
STATUSES = ["正常", "延期修复", "已关闭"]
TOPICS = ["登录", "表单", "列表", "支付", "搜索", "权限", "通知", "导出"]


def _random_created(base: datetime, day_offset: int) -> str:
    dt = base + timedelta(days=day_offset, hours=random.randint(8, 18), minutes=random.choice([0, 15, 30, 45]))
    return dt.strftime("%Y-%m-%d %H:%M")


def generate_rows(count: int, seed: int | None = 42) -> list[dict]:
    if seed is not None:
        random.seed(seed)

    rows = [dict(r) for r in BASE_ISSUES]
    base_date = datetime(2026, 5, 16)
    next_id = len(rows) + 1

    while len(rows) < count:
        assignee = random.choice(ASSIGNEES)
        issue_type = random.choice(TYPES)
        status = random.choice(STATUSES)
        topic = random.choice(TOPICS)
        priority = random.randint(1, 10)
        hours = random.randint(4, 72)

        rows.append(
            {
                "id": next_id,
                "description": f"{assignee}：{topic}相关{issue_type.replace('问题', '')}异常",
                "assignee": assignee,
                "type": issue_type,
                "created": _random_created(base_date, random.randint(0, 14)),
                "status": status,
                "priority_score": priority,
                "resolve_hours": hours,
            }
        )
        next_id += 1

    return rows[:count]


def write_outputs(path: Path, count: int, seed: int | None) -> pd.DataFrame:
    """生成 CSV / JSON / data.js，供 Python 绘图与 HTML 页面共用。"""
    import json

    df = pd.DataFrame(generate_rows(count, seed))
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")

    records = df.to_dict(orient="records")
    json_path = path.with_suffix(".json")
    json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    js_path = path.parent / "data.js"
    js_path.write_text(
        f"const ISSUES_DATA = {json.dumps(records, ensure_ascii=False, indent=2)};\n",
        encoding="utf-8",
    )
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 data.csv 测试物料")
    parser.add_argument("-o", "--output", default="data.csv", help="输出路径，默认 data.csv")
    parser.add_argument("-n", "--count", type=int, default=20, help="生成行数，默认 20")
    parser.add_argument("--seed", type=int, default=42, help="随机种子，便于复现")
    args = parser.parse_args()

    out = Path(args.output)
    write_outputs(out, args.count, args.seed)
    print(f"已生成 {out.resolve()}，共 {args.count} 行")
    print(f"已生成 {out.with_suffix('.json').resolve()}")
    print(f"已生成 {(out.parent / 'data.js').resolve()}")


if __name__ == "__main__":
    main()
