#!/usr/bin/env python3
"""数据加载、处理与可视化工具。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib


def _configure_matplotlib_backend() -> None:
    """无 --show 时用 Agg 仅保存文件；有 --show 时切换为可弹窗的 GUI 后端。"""
    if "--show" not in sys.argv:
        matplotlib.use("Agg")
        return

    candidates = (
        ("MacOSX", "TkAgg", "Qt5Agg")
        if sys.platform == "darwin"
        else ("TkAgg", "Qt5Agg", "MacOSX")
    )
    for name in candidates:
        try:
            matplotlib.use(name)
            return
        except ImportError:
            continue


_configure_matplotlib_backend()
import matplotlib.pyplot as plt
import pandas as pd

# 中文显示（系统无对应字体时会回退到默认字体）
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti SC", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

# 常见别名 → data.csv 中的实际列名
COLUMN_ALIASES = {
    "category": "type",
    "类别": "type",
    "类型": "type",
    "负责人": "assignee",
    "跟进人": "assignee",
    "状态": "status",
    "优先级": "priority_score",
    "处理时长": "resolve_hours",
}


class DataPlotter:
    """封装常见数据处理与绘图操作。"""

    def __init__(self, df: pd.DataFrame | None = None):
        self.df = df.copy() if df is not None else pd.DataFrame()

    @classmethod
    def from_file(cls, path: str | Path, **read_kwargs: Any) -> DataPlotter:
        path = Path(path)
        suffix = path.suffix.lower()

        if suffix == ".csv":
            df = pd.read_csv(path, **read_kwargs)
        elif suffix in {".xlsx", ".xls"}:
            df = pd.read_excel(path, **read_kwargs)
        elif suffix == ".json":
            df = pd.read_json(path, **read_kwargs)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")

        return cls(df)

    def drop_na(self, subset: list[str] | None = None) -> DataPlotter:
        self.df = self.df.dropna(subset=subset)
        return self

    def resolve_column(self, name: str | None) -> str | None:
        """解析列名；支持别名，不存在时给出可用列提示。"""
        if name is None:
            return None
        if name in self.df.columns:
            return name
        mapped = COLUMN_ALIASES.get(name)
        if mapped and mapped in self.df.columns:
            return mapped
        available = ", ".join(self.df.columns.astype(str))
        hint = ""
        if name == "category":
            hint = "（示例中的 category 对应本文件的 type 列）"
        raise SystemExit(f"列 '{name}' 不存在{hint}。可用列: {available}")

    def require_columns(self, *names: str | None) -> tuple[str | None, ...]:
        return tuple(self.resolve_column(n) for n in names)

    def filter_rows(self, query: str) -> DataPlotter:
        """使用 pandas query 语法筛选，例如 `status == '正常'`。"""
        self.df = self.df.query(query)
        return self

    def group_count(self, column: str, sort: bool = True) -> pd.Series:
        counts = self.df[column].value_counts()
        return counts.sort_values(ascending=False) if sort else counts

    def plot_line(
        self,
        x: str,
        y: str | list[str],
        title: str = "",
        figsize: tuple[float, float] = (10, 5),
    ) -> plt.Figure:
        fig, ax = plt.subplots(figsize=figsize)
        ys = [y] if isinstance(y, str) else y
        for col in ys:
            ax.plot(self.df[x], self.df[col], marker="o", label=col)
        ax.set_xlabel(x)
        ax.set_ylabel(" / ".join(ys))
        ax.set_title(title or f"{x} vs {', '.join(ys)}")
        if len(ys) > 1:
            ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        return fig

    def plot_bar(
        self,
        x: str,
        y: str | None = None,
        title: str = "",
        horizontal: bool = False,
        figsize: tuple[float, float] = (10, 5),
    ) -> plt.Figure:
        fig, ax = plt.subplots(figsize=figsize)
        if y is None:
            series = self.group_count(x)
            labels, values = series.index.tolist(), series.values.tolist()
            plot_fn = ax.barh if horizontal else ax.bar
            plot_fn(labels, values, color="#3b82f6", edgecolor="white")
            ax.set_xlabel("数量" if horizontal else x)
            ax.set_ylabel(x if horizontal else "数量")
            ax.set_title(title or f"{x} 分布")
        else:
            plot_fn = ax.barh if horizontal else ax.bar
            plot_fn(self.df[x], self.df[y], color="#3b82f6", edgecolor="white")
            ax.set_xlabel(x)
            ax.set_ylabel(y)
            ax.set_title(title or f"{y} by {x}")
        fig.tight_layout()
        return fig

    def plot_scatter(
        self,
        x: str,
        y: str,
        hue: str | None = None,
        title: str = "",
        figsize: tuple[float, float] = (8, 6),
    ) -> plt.Figure:
        fig, ax = plt.subplots(figsize=figsize)
        if hue and hue in self.df.columns:
            for name, group in self.df.groupby(hue):
                ax.scatter(group[x], group[y], label=str(name), alpha=0.75)
            ax.legend(title=hue)
        else:
            ax.scatter(self.df[x], self.df[y], alpha=0.75, color="#6366f1")
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_title(title or f"{x} vs {y}")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        return fig

    def plot_pie(
        self,
        column: str,
        title: str = "",
        figsize: tuple[float, float] = (8, 8),
    ) -> plt.Figure:
        counts = self.group_count(column)
        fig, ax = plt.subplots(figsize=figsize)
        ax.pie(
            counts.values,
            labels=counts.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=plt.cm.Set3.colors,
        )
        ax.set_title(title or f"{column} 占比")
        fig.tight_layout()
        return fig

    def plot_hist(
        self,
        column: str,
        bins: int = 20,
        title: str = "",
        figsize: tuple[float, float] = (10, 5),
    ) -> plt.Figure:
        fig, ax = plt.subplots(figsize=figsize)
        ax.hist(self.df[column].dropna(), bins=bins, color="#10b981", edgecolor="white")
        ax.set_xlabel(column)
        ax.set_ylabel("频数")
        ax.set_title(title or f"{column} 直方图")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        return fig

    def save(self, fig: plt.Figure, path: str | Path, dpi: int = 150) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        return path


def sample_issues_df() -> pd.DataFrame:
    """与 index.html 中问题列表示例一致的数据。"""
    return pd.DataFrame(
        [
            {"assignee": "张三", "type": "功能问题", "status": "延期修复"},
            {"assignee": "李四", "type": "体验问题", "status": "正常"},
            {"assignee": "王五", "type": "功能问题", "status": "延期修复"},
            {"assignee": "赵六", "type": "体验问题", "status": "正常"},
        ]
    )


def run_demo(output_dir: Path) -> None:
    plotter = DataPlotter(sample_issues_df())
    output_dir.mkdir(parents=True, exist_ok=True)

    charts = [
        ("type_bar.png", plotter.plot_bar("type", title="问题类型分布")),
        ("status_pie.png", plotter.plot_pie("status", title="问题状态占比")),
        ("assignee_bar.png", plotter.plot_bar("assignee", title="跟进人问题数")),
    ]

    for name, fig in charts:
        out = plotter.save(fig, output_dir / name)
        plt.close(fig)
        print(f"已保存: {out}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="数据加载、处理与绘图")
    parser.add_argument("--input", "-i", help="输入文件路径 (csv / json / xlsx)")
    parser.add_argument("--chart", "-c", choices=["line", "bar", "scatter", "pie", "hist"], required=False)
    parser.add_argument("--x", help="X 轴或分类列名")
    parser.add_argument("--y", help="Y 轴列名（line/bar/scatter/hist 需要）")
    parser.add_argument("--hue", help="散点图分组列")
    parser.add_argument("--query", "-q", help="筛选条件，如 status == '正常'")
    parser.add_argument("--output", "-o", default="output/chart.png", help="输出图片路径")
    parser.add_argument("--title", "-t", default="", help="图表标题")
    parser.add_argument("--demo", action="store_true", help="使用示例数据生成多张图")
    parser.add_argument("--show", action="store_true", help="显示图表窗口")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.demo:
        run_demo(Path("output"))
        return

    if not args.input or not args.chart:
        print("请指定 --input 与 --chart，或使用 --demo 查看示例。")
        return

    plotter = DataPlotter.from_file(args.input)
    if args.query:
        plotter.filter_rows(args.query)

    if args.chart == "pie" and not args.x:
        raise SystemExit("饼图需要 --x 指定分类列")
    if args.chart in {"line", "scatter", "hist"} and (not args.x or not args.y):
        if args.chart == "hist":
            args.y = args.x
        else:
            raise SystemExit(f"{args.chart} 图需要 --x 与 --y")
    if args.chart == "bar" and not args.x:
        raise SystemExit("柱状图需要 --x")

    args.x, args.y, args.hue = plotter.require_columns(args.x, args.y, args.hue)

    plotters = {
        "line": lambda: plotter.plot_line(args.x, args.y, title=args.title),
        "bar": lambda: plotter.plot_bar(args.x, args.y, title=args.title),
        "scatter": lambda: plotter.plot_scatter(args.x, args.y, hue=args.hue, title=args.title),
        "pie": lambda: plotter.plot_pie(args.x, title=args.title),
        "hist": lambda: plotter.plot_hist(args.x, title=args.title),
    }

    fig = plotters[args.chart]()
    out = plotter.save(fig, args.output)
    print(f"已保存: {out}")

    if args.show:
        plt.show()
    else:
        plt.close(fig)


if __name__ == "__main__":
    main()
