#!/usr/bin/env python3
"""Validate every skills/*/SKILL.md against the Agent Skills spec and repo rules."""
import re, sys, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
errors, names = [], set()
for f in sorted((root / "skills").glob("*/SKILL.md")):
    text = f.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{f}: no frontmatter"); continue
    fm = {}
    for line in m.group(1).split("\n"):
        k = re.match(r"^([a-z-]+):\s*(.*)$", line)
        if k: fm[k.group(1)] = k.group(2).strip().strip('"')
    name, desc = fm.get("name", ""), fm.get("description", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        errors.append(f"{f}: bad name {name!r}")
    if name != f.parent.name: errors.append(f"{f}: name differs from folder")
    if name in names: errors.append(f"{f}: duplicate name")
    names.add(name)
    if not desc or len(desc) > 1024: errors.append(f"{f}: description length {len(desc)}")
    if len(text.splitlines()) > 500: errors.append(f"{f}: over 500 lines")
    print(f"ok {name}: description {len(desc)} chars, {len(text.splitlines())} lines")
for p in root.rglob("*"):
    if p.is_file() and ".git" not in p.parts and p.suffix in {".md", ".txt", ".py"}:
        t = p.read_text(encoding="utf-8")
        if chr(0x2014) in t or chr(0x2013) in t: errors.append(f"{p}: em or en dash")
if errors:
    print("\n".join(errors)); sys.exit(1)
print(f"{len(names)} skills valid")
