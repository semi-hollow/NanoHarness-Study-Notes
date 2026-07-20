#!/usr/bin/env python3
"""在任意 NanoHarness checkout 中安装低噪音 PyCharm 导航配置。"""

from __future__ import annotations

import argparse
import shutil
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


TEST_ROOT = "file://$MODULE_DIR$/tests"
EXCLUDED_ROOTS = (
    ".agent_forge",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "build",
    "dist",
)


@dataclass(frozen=True)
class ScopeSpec:
    """一份可在 Project、Find Usages 和 Call Hierarchy 中复用的文件集合。"""

    filename: str
    name: str
    pattern: str


SCOPES = (
    ScopeSpec(
        "00_NanoHarness_Review_Path.xml",
        "00 NanoHarness Review Path",
        "file:agent_forge/harness.py||file:agent_forge/runtime/wiring.py||"
        "file:agent_forge/runtime/application/agent_loop.py||"
        "file:agent_forge/runtime/application/session.py||"
        "file:agent_forge/runtime/application/turn_preparation.py||"
        "file:agent_forge/runtime/application/tool_execution.py||"
        "file:agent_forge/runtime/application/operation_tracker.py||"
        "file:agent_forge/runtime/application/run_lifecycle.py||"
        "file:agent_forge/runtime/domain/task.py||"
        "file:agent_forge/runtime/domain/operation.py||"
        "file:agent_forge/observability/domain/event.py||"
        "file:agent_forge/observability/domain/run_story.py",
    ),
    ScopeSpec(
        "10_NanoHarness_Production_Code.xml",
        "10 NanoHarness Production Code",
        "file:agent_forge//*||file:examples//*||file:scripts//*",
    ),
    ScopeSpec(
        "20_NanoHarness_Runtime_Control_Plane.xml",
        "20 NanoHarness Runtime Control Plane",
        "file:agent_forge/harness.py||file:agent_forge/configuration.py||"
        "file:agent_forge/control.py||file:agent_forge/hooks.py||"
        "file:agent_forge/runtime//*||file:agent_forge/context//*||"
        "file:agent_forge/tools//*||file:agent_forge/safety//*||"
        "file:agent_forge/multi_agent//*",
    ),
    ScopeSpec(
        "30_NanoHarness_Evaluation_Loop.xml",
        "30 NanoHarness Evaluation Loop",
        "file:agent_forge/bench//*||file:agent_forge/evaluation//*||"
        "file:agent_forge/observability//*",
    ),
    ScopeSpec(
        "90_NanoHarness_Tests.xml",
        "90 NanoHarness Tests",
        "file:tests//*",
    ),
)


def scope_tree(spec: ScopeSpec) -> ET.ElementTree:
    """构造 PyCharm 共享 Scope 的稳定 XML。"""
    root = ET.Element("component", {"name": "DependencyValidationManager"})
    ET.SubElement(root, "scope", {"name": spec.name, "pattern": spec.pattern})
    return ET.ElementTree(root)


def scope_matches(path: Path, spec: ScopeSpec) -> bool:
    """按语义比较 Scope，避免仅因 XML 排版不同重复覆盖。"""
    if not path.is_file():
        return False
    try:
        scope = ET.parse(path).getroot().find("scope")
    except ET.ParseError:
        return False
    return scope is not None and scope.attrib == {"name": spec.name, "pattern": spec.pattern}


def find_module_file(idea_dir: Path) -> Path:
    """找到 PyCharm 首次打开项目后创建的唯一模块文件。"""
    module_files = sorted(idea_dir.glob("*.iml"))
    if len(module_files) != 1:
        raise RuntimeError(
            f"期望 .idea 中恰好一个 .iml，实际为 {len(module_files)}；"
            "请先用 PyCharm 打开 NanoHarness，再重新运行。"
        )
    return module_files[0]


def module_gaps(module_file: Path) -> list[str]:
    """返回 Test Sources 与索引排除项中仍缺少的配置。"""
    try:
        root = ET.parse(module_file).getroot()
    except ET.ParseError as exc:
        raise RuntimeError(f"无法解析 {module_file}: {exc}") from exc
    manager = root.find("./component[@name='NewModuleRootManager']")
    if manager is None:
        return ["NewModuleRootManager", "tests Test Sources", *EXCLUDED_ROOTS]
    content = manager.find("./content[@url='file://$MODULE_DIR$']")
    if content is None:
        return ["project content root", "tests Test Sources", *EXCLUDED_ROOTS]

    gaps: list[str] = []
    test_root = content.find(f"./sourceFolder[@url='{TEST_ROOT}']")
    if test_root is None or test_root.get("isTestSource") != "true":
        gaps.append("tests Test Sources")
    existing_excludes = {item.get("url") for item in content.findall("excludeFolder")}
    for folder in EXCLUDED_ROOTS:
        if f"file://$MODULE_DIR$/{folder}" not in existing_excludes:
            gaps.append(folder)
    return gaps


def install_module_roots(module_file: Path) -> bool:
    """保留已有 SDK/组件，只补测试源和应排除的生成目录。"""
    tree = ET.parse(module_file)
    root = tree.getroot()
    root.set("type", root.get("type", "PYTHON_MODULE"))
    manager = root.find("./component[@name='NewModuleRootManager']")
    if manager is None:
        manager = ET.SubElement(root, "component", {"name": "NewModuleRootManager"})
        ET.SubElement(manager, "orderEntry", {"type": "inheritedJdk"})
        ET.SubElement(manager, "orderEntry", {"type": "sourceFolder", "forTests": "false"})
    content = manager.find("./content[@url='file://$MODULE_DIR$']")
    if content is None:
        content = ET.Element("content", {"url": "file://$MODULE_DIR$"})
        manager.insert(0, content)

    changed = False
    test_root = content.find(f"./sourceFolder[@url='{TEST_ROOT}']")
    if test_root is None:
        test_root = ET.SubElement(content, "sourceFolder", {"url": TEST_ROOT})
        changed = True
    if test_root.get("isTestSource") != "true":
        test_root.set("isTestSource", "true")
        changed = True

    existing_excludes = {item.get("url") for item in content.findall("excludeFolder")}
    for folder in EXCLUDED_ROOTS:
        url = f"file://$MODULE_DIR$/{folder}"
        if url not in existing_excludes:
            ET.SubElement(content, "excludeFolder", {"url": url})
            changed = True

    if changed:
        backup = module_file.with_suffix(f"{module_file.suffix}.before-navigation-setup")
        if not backup.exists():
            shutil.copy2(module_file, backup)
        ET.indent(tree, space="  ")
        tree.write(module_file, encoding="UTF-8", xml_declaration=True)
    return changed


def validate_project(project_dir: Path) -> Path:
    """拒绝把配置误装到其他仓库。"""
    root = project_dir.expanduser().resolve()
    if not (root / "agent_forge").is_dir() or not (root / "tests").is_dir():
        raise RuntimeError(f"{root} 不是 NanoHarness checkout")
    return root


def check_installation(project_dir: Path) -> list[str]:
    """检查另一台设备是否已经获得同样的低噪音导航环境。"""
    idea_dir = project_dir / ".idea"
    module_file = find_module_file(idea_dir)
    gaps = [f"模块配置缺少: {item}" for item in module_gaps(module_file)]
    scopes_dir = idea_dir / "scopes"
    for spec in SCOPES:
        if not scope_matches(scopes_dir / spec.filename, spec):
            gaps.append(f"Scope 缺少或过时: {spec.name}")
    return gaps


def install(project_dir: Path) -> None:
    """主要入口：安装配置后立即执行一次完整校验。"""
    idea_dir = project_dir / ".idea"
    module_file = find_module_file(idea_dir)
    scopes_dir = idea_dir / "scopes"
    scopes_dir.mkdir(parents=True, exist_ok=True)
    for spec in SCOPES:
        target = scopes_dir / spec.filename
        if not scope_matches(target, spec):
            tree = scope_tree(spec)
            ET.indent(tree, space="  ")
            tree.write(target, encoding="UTF-8", xml_declaration=False)
    install_module_roots(module_file)

    gaps = check_installation(project_dir)
    if gaps:
        raise RuntimeError("安装后校验失败：\n- " + "\n- ".join(gaps))
    print(f"PyCharm 低噪音导航配置已就绪：{project_dir}")


def parse_args() -> argparse.Namespace:
    """解析跨设备安装或只读检查参数。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="NanoHarness checkout 路径")
    parser.add_argument("--check", action="store_true", help="只检查，不修改本地 .idea")
    return parser.parse_args()


def main() -> int:
    """命令行入口：错误信息保持可直接行动。"""
    args = parse_args()
    try:
        project_dir = validate_project(args.project)
        if args.check:
            gaps = check_installation(project_dir)
            if gaps:
                print("PyCharm 导航配置未就绪：")
                for gap in gaps:
                    print(f"- {gap}")
                return 1
            print(f"PyCharm 低噪音导航配置检查通过：{project_dir}")
            return 0
        install(project_dir)
        return 0
    except RuntimeError as exc:
        print(f"配置失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
