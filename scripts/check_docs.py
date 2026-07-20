#!/usr/bin/env python3
"""校验学习仓库的文档边界，防止重复资料重新扩张。"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]

# 每个主题只有一个 owner。新增文档前必须先修改 README 中的治理规则。
LINE_BUDGETS = {
    "README.md": 120,
    "learning/01-系统地图与代码入口.md": 235,
    "learning/02-核心机制与设计边界.md": 220,
    "learning/03-Benchmark与证据闭环.md": 210,
    "learning/04-闭卷自测与反馈.md": 220,
    "interview/demo/五分钟面试演示脚本.md": 160,
    "interview/strategy/2026-07-19_北京Agent招聘市场与NanoHarness定位.md": 180,
    "interview/references/Clowder_AI_Agent_面经精练版.md": 350,
}

# 一手记录不是学习材料的重复副本。缺失或被压成摘要都应阻断 CI。
PROTECTED_RECORDS = {
    "records/interviews/2026-07-17_NanoHarness模拟面试复盘与标准回答.md": (180, 260),
}

REQUIRED_SUPPORT_FILES = (
    "scripts/install_pycharm_navigation.py",
)

REQUIRED_SECTIONS = {
    "learning/01-系统地图与代码入口.md": ("## 闭卷检查",),
    "learning/02-核心机制与设计边界.md": ("## 闭卷检查",),
    "learning/03-Benchmark与证据闭环.md": ("## 闭卷检查",),
    "learning/04-闭卷自测与反馈.md": ("## 闭卷问题", "## 复测记录"),
    "interview/demo/五分钟面试演示脚本.md": ("## 演示后自评",),
    "interview/strategy/2026-07-19_北京Agent招聘市场与NanoHarness定位.md": ("## 自检",),
    "records/interviews/2026-07-17_NanoHarness模拟面试复盘与标准回答.md": (
        "## 二、问题诊断表",
        "## 六、项目问题与本轮处理结果",
    ),
}

MARKDOWN_LINK = re.compile(r"(?<!!)\[[^]]*]\(([^)]+)\)")


def tracked_markdown_files() -> set[str]:
    """返回 Git 当前会提交的 Markdown，忽略本地归档和已删除文件。"""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return {
        path
        for path in result.stdout.decode("utf-8").split("\0")
        if path.endswith(".md") and (ROOT / path).is_file()
    }


def local_link_errors(relative_path: str, content: str) -> list[str]:
    """检查 Markdown 相对链接，不把 URL、邮箱和页内锚点当成本地文件。"""
    errors: list[str] = []
    source = ROOT / relative_path
    for raw_target in MARKDOWN_LINK.findall(content):
        target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path_part = unquote(target.split("#", 1)[0])
        if path_part and not (source.parent / path_part).resolve().exists():
            errors.append(f"{relative_path}: 失效链接 {raw_target}")
    return errors


def collect_errors() -> list[str]:
    """执行结构、体量、反馈入口和链接四类校验。"""
    errors: list[str] = []
    expected = set(LINE_BUDGETS) | set(PROTECTED_RECORDS)
    actual = tracked_markdown_files()

    for path in sorted(actual - expected):
        errors.append(f"未归类 Markdown: {path}")
    for path in sorted(set(LINE_BUDGETS) - actual):
        errors.append(f"缺少受控文档: {path}")
    for path in sorted(set(PROTECTED_RECORDS) - actual):
        errors.append(f"受保护的一手记录被删除: {path}")
    for relative_path in REQUIRED_SUPPORT_FILES:
        if not (ROOT / relative_path).is_file():
            errors.append(f"缺少学习辅助工具: {relative_path}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    all_budgets = {
        **LINE_BUDGETS,
        **{path: maximum for path, (_, maximum) in PROTECTED_RECORDS.items()},
    }
    for relative_path, limit in all_budgets.items():
        path = ROOT / relative_path
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        line_count = len(content.splitlines())
        if line_count > limit:
            errors.append(f"{relative_path}: {line_count} 行，超过 {limit} 行上限")
        minimum = PROTECTED_RECORDS.get(relative_path, (0, limit))[0]
        if line_count < minimum:
            errors.append(f"{relative_path}: 受保护记录只剩 {line_count} 行，低于 {minimum} 行")
        for heading in REQUIRED_SECTIONS.get(relative_path, ()):
            if heading not in content:
                errors.append(f"{relative_path}: 缺少反馈入口 {heading}")
        if relative_path != "README.md" and relative_path not in readme:
            errors.append(f"README 未链接受控文档: {relative_path}")
        errors.extend(local_link_errors(relative_path, content))
    return errors


def main() -> int:
    """主要入口：输出可直接修复的错误，并以退出码供 CI 判定。"""
    errors = collect_errors()
    if errors:
        print("文档治理检查失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"文档治理检查通过：{len(LINE_BUDGETS)} 份主动学习文档，"
        f"{len(PROTECTED_RECORDS)} 份受保护的一手记录。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
