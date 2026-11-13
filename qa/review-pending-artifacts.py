#!/usr/bin/env python3
"""Read-only semantic review of selected unresolved generated-asset PRs.

This is diagnostic evidence, not an automated merge/close decision:
show changed PDF page text, editable PPTX slide text, and selected WebP pixels.
All files are fetched by exact SHA; no reference is modified.
"""
from __future__ import annotations

import base64
import difflib
import io
import json
import os
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from functools import lru_cache
from pathlib import Path

import fitz
from PIL import Image, ImageChops

REPO = os.getenv("GITHUB_REPOSITORY", "dohyunkimmm/mosigo-case-study")
TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
TARGETS = [142, 154, 153, 139, 135]
OUT = Path("qa-artifacts/unresolved-asset-review.json")
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def api(path):
    request = urllib.request.Request(
        "https://api.github.com/" + path.lstrip("/"),
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "mosigo-pending-asset-review",
            "Authorization": "Bearer " + TOKEN,
        },
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


@lru_cache(maxsize=100)
def blob(sha):
    item = api(f"repos/{REPO}/git/blobs/{sha}")
    if item["encoding"] != "base64":
        raise RuntimeError("Not a supported Git binary blob " + sha)
    return base64.b64decode(item["content"])


def cleaned_lines(text):
    return [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()
            if line.strip()]


def changed_lines(left, right):
    before = cleaned_lines(left)
    after = cleaned_lines(right)
    matcher = difflib.SequenceMatcher(a=before, b=after, autojunk=False)
    removed, added, change_blocks = [], [], 0
    for tag, i0, i1, j0, j1 in matcher.get_opcodes():
        if tag == "equal":
            continue
        change_blocks += 1
        removed.extend(before[i0:i1])
        added.extend(after[j0:j1])
    return {
        "changed": bool(change_blocks),
        "removed_line_count": len(removed),
        "added_line_count": len(added),
        "removed_examples": removed[:8],
        "added_examples": added[:8],
    }


def pdf_comparison(before, after):
    with fitz.open(stream=before, filetype="pdf") as old, \
         fitz.open(stream=after, filetype="pdf") as new:
        old_page_count, new_page_count = old.page_count, new.page_count
        changed = []
        for number in range(max(old_page_count, new_page_count)):
            if number >= old_page_count or number >= new_page_count:
                changed.append({"page": number + 1, "reason": "added or deleted page"})
                continue
            a = old[number].get_text("text", sort=True)
            b = new[number].get_text("text", sort=True)
            diff = changed_lines(a, b)
            if diff["changed"]:
                changed.append({"page": number + 1, **diff})
        return {
            "type": "PDF",
            "before_pages": old_page_count,
            "after_pages": new_page_count,
            "text_changed_pages": len(changed),
            "page_changes": changed[:14],
            "exhaustive_text_comparison": True,
            "pixel_comparison": "See existing strict whole-artifact audit; not used for close decision",
        }


def pptx_slide_texts(data):
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        slides = sorted(
            (name for name in package.namelist()
             if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)),
            key=lambda name: int(re.search(r"slide(\d+)", name).group(1)),
        )
        result = []
        for name in slides:
            root = ET.fromstring(package.read(name))
            texts = [node.text or "" for node in root.findall(".//a:t", NS)]
            result.append("\n".join(t for t in texts if t.strip()))
        return result


def pptx_comparison(before, after):
    old = pptx_slide_texts(before)
    new = pptx_slide_texts(after)
    changed = []
    for idx in range(max(len(old), len(new))):
        if idx >= len(old) or idx >= len(new):
            changed.append({"slide": idx + 1, "reason": "added or deleted slide"})
            continue
        diff = changed_lines(old[idx], new[idx])
        if diff["changed"]:
            changed.append({"slide": idx + 1, **diff})
    return {
        "type": "PPTX",
        "before_slides": len(old),
        "after_slides": len(new),
        "changed_text_slides": len(changed),
        "slide_changes": changed[:14],
        "exhaustive_slide_text_comparison": True,
        "visual_and_editability_equivalence": "not established",
    }


def image_comparison(before, after):
    with Image.open(io.BytesIO(before)) as image_a, \
         Image.open(io.BytesIO(after)) as image_b:
        a = image_a.convert("RGB")
        b = image_b.convert("RGB")
        if a.size != b.size:
            return {
                "type": "WebP",
                "before_size": list(a.size),
                "after_size": list(b.size),
                "same_dimensions": False,
            }
        diff = ImageChops.difference(a, b)
        histogram = diff.histogram()
        total = a.width * a.height * 3
        weighted = sum((i % 256) * count for i, count in enumerate(histogram))
        diff_abs = sum(count for i, count in enumerate(histogram) if i % 256 >= 8)
        return {
            "type": "WebP",
            "same_dimensions": True,
            "dimensions": list(a.size),
            "mean_channel_absolute_diff": round(weighted / total, 3),
            "fraction_channels_difference_ge_8": round(diff_abs / total, 4),
            "interpretation": "diagnostic only: no automatic visual equivalence",
        }


def main():
    if not TOKEN:
        raise RuntimeError("GH_TOKEN is required")
    main_tree = api(f"repos/{REPO}/git/trees/main?recursive=1")
    if main_tree.get("truncated"):
        raise RuntimeError("Git tree truncated")
    baseline = {
        x["path"]: x["sha"] for x in main_tree["tree"]
        if x["type"] == "blob"
    }
    report = {
        "repo": REPO,
        "main_tree": main_tree["sha"],
        "targets": TARGETS,
        "method": "Exact blobs; full PDF and PPTX text, first 6 changed WebP samples per PR",
        "reviews": [],
    }
    for number in TARGETS:
        pr = api(f"repos/{REPO}/pulls/{number}")
        files = api(f"repos/{REPO}/pulls/{number}/files?per_page=100")
        if len(files) == 100:
            raise RuntimeError(f"PR {number} requires pagination")
        item = {
            "pr": number,
            "title": pr["title"],
            "state": pr["state"],
            "draft": pr["draft"],
            "head_sha": pr["head"]["sha"],
            "files_total": len(files),
            "documents": [],
            "webp_sample": [],
            "html_paths": [],
            "errors": [],
        }
        image_count = 0
        for file in files:
            path = file["filename"]
            suffix = Path(path).suffix.lower()
            current = baseline.get(path)
            proposed = file.get("sha")
            if suffix in {".html", ".htm"}:
                item["html_paths"].append(path)
                continue
            if suffix == ".webp" and image_count >= 6:
                continue
            if suffix not in {".pdf", ".pptx", ".webp"}:
                continue
            if not current or not proposed or file["status"] != "modified":
                item["errors"].append({"path": path, "reason": "missing baseline or addition"})
                continue
            try:
                if suffix == ".pdf":
                    summary = pdf_comparison(blob(current), blob(proposed))
                    item["documents"].append({"path": path, **summary})
                elif suffix == ".pptx":
                    summary = pptx_comparison(blob(current), blob(proposed))
                    item["documents"].append({"path": path, **summary})
                else:
                    summary = image_comparison(blob(current), blob(proposed))
                    item["webp_sample"].append({"path": path, **summary})
                    image_count += 1
            except Exception as exc:
                item["errors"].append({"path": path, "error": str(exc)[:300]})
        report["reviews"].append(item)
        for doc in item["documents"]:
            n = doc.get("text_changed_pages", doc.get("changed_text_slides", "?"))
            total = doc.get("after_pages", doc.get("after_slides", "?"))
            print(f"PR #{number} {doc['path']}: {n}/{total} pages/slides with text differences", flush=True)
            for change in (doc.get("page_changes") or doc.get("slide_changes") or [])[:4]:
                print("  ", "page/slide", change.get("page",change.get("slide")),
                      "removed:", change.get("removed_examples",[])[:2],
                      "added:", change.get("added_examples",[])[:2], flush=True)
        for asset in item["webp_sample"]:
            print(f"PR #{number} {asset['path']}: mean pixel/channel delta "
                  f"{asset.get('mean_channel_absolute_diff','dimensions differ')}", flush=True)
        if item["errors"]:
            print(f"PR #{number} errors: {item['errors']}", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS read-only review; no PRs were merged, closed or deleted.", flush=True)


if __name__ == "__main__":
    main()
