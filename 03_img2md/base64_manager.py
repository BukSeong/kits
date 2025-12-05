import argparse
import os
import re
import sys
from typing import Dict, List, Set, Tuple

# Regex to match lines like [image-1]:data:image/png;base64,xxxx
BASE64_REF_PATTERN = re.compile(r"^\s*\[([^\]]+)\]:\s*data:image/[^;]+;base64,.*$")


def read_markdown(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


def write_markdown(path: str, lines: List[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def find_image_refs(lines: List[str]) -> Dict[str, List[int]]:
    """Return mapping of image-id -> list of line indices (0-based) that contain its base64 ref."""
    hits: Dict[str, List[int]] = {}
    for idx, line in enumerate(lines):
        m = BASE64_REF_PATTERN.match(line)
        if not m:
            continue
        image_id = m.group(1).strip()
        hits.setdefault(image_id, []).append(idx)
    return hits


def parse_idx_arg(idx_arg: str) -> Set[str]:
    if not idx_arg:
        return set()
    parts = re.split(r"[\s,;]+", idx_arg)
    return {p.strip() for p in parts if p.strip()}


def prompt_md_path(md_path: str) -> str:
    if md_path:
        return md_path
    return input("请输入Markdown文件路径 (--md-dir): ").strip().strip('\"\'')


def prompt_ids(hits: Dict[str, List[int]]) -> Set[str]:
    if not hits:
        return set()
    raw = input("输入要删除的image-id，可用逗号/空格分隔（回车跳过）：").strip()
    return parse_idx_arg(raw)


def remove_ids(lines: List[str], targets: Set[str]) -> Tuple[List[str], Set[str]]:
    kept: List[str] = []
    removed: Set[str] = set()
    for line in lines:
        m = BASE64_REF_PATTERN.match(line)
        if m and m.group(1).strip() in targets:
            removed.add(m.group(1).strip())
            continue
        kept.append(line)
    return kept, removed


def main() -> None:
    parser = argparse.ArgumentParser(description="列出并删除Markdown中的Base64图片引用行")
    parser.add_argument("--md-dir", default=None, help="Markdown文件路径")
    parser.add_argument("--idx", default=None, help="要删除的image-id，支持逗号/空格分隔多个")
    args = parser.parse_args()

    md_path = prompt_md_path(args.md_dir)
    md_path = md_path.strip('\"\'')
    if not md_path:
        print("错误: 未提供Markdown文件路径")
        sys.exit(1)
    if not os.path.exists(md_path):
        print(f"错误: 找不到Markdown文件: {md_path}")
        sys.exit(1)

    lines = read_markdown(md_path)
    hits = find_image_refs(lines)

    if not hits:
        print(f"在 {md_path} 中未找到Base64图片引用。")
        return

    print(f"在 {md_path} 中找到以下Base64图片引用:")
    for image_id, idx_list in sorted(hits.items(), key=lambda x: x[0]):
        human_lines = ",".join(str(i + 1) for i in idx_list)
        print(f"- {image_id} (行: {human_lines})")

    targets = parse_idx_arg(args.idx) if args.idx else prompt_ids(hits)
    if not targets:
        print("未指定要删除的 image-id，退出。")
        return

    unknown = targets - set(hits.keys())
    if unknown:
        print(f"警告: 下列 image-id 未在文件中找到，将被忽略: {', '.join(sorted(unknown))}")
    valid_targets = targets & set(hits.keys())
    if not valid_targets:
        print("没有可删除的 image-id。")
        return

    new_lines, removed = remove_ids(lines, valid_targets)
    write_markdown(md_path, new_lines)

    print(f"已删除 {len(removed)} 条Base64引用: {', '.join(sorted(removed))}")


if __name__ == "__main__":
    main()
