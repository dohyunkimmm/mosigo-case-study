#!/usr/bin/env python3
"""Read-only visual/content audit of the four remaining generated MOSIGO PRs.

The job does not merge, close, publish or change any Git ref.
Creates labeled before/after document-page contact sheets and a JSON report.
Exact PR head blob IDs avoid confusion with old merge bases.
"""
from __future__ import annotations

import base64
import io
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from functools import lru_cache
from pathlib import Path

import fitz
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps
from pptx import Presentation

REPO = os.environ.get("GITHUB_REPOSITORY", "dohyunkimmm/mosigo-case-study")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
ROOT = Path("qa-artifacts/final-four-visual-audit")
PR_ASSETS = {
    139: ["downloads/mosigo_business_plan_20261031.pdf"],
    154: ["downloads/mosigo_report_preview.pdf"],
    135: [
        "downloads/MOSIGO_IR_Investment_Review_12slides.pdf",
        "downloads/MOSIGO_IR_Investment_Review_12slides.pptx",
    ],
    153: [],
}


def api(path):
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/{path.lstrip('/')}",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "mosigo-last-four-visual-review",
        }
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == 4:
                raise RuntimeError("GitHub API failed: " + path) from exc
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


@lru_cache(maxsize=160)
def blob(sha):
    content = api(f"git/blobs/{sha}")
    if content.get("encoding") != "base64":
        raise RuntimeError(f"Unexpected encoding for SHA {sha}")
    return base64.b64decode(content["content"])


def changed_files(number):
    items = api(f"pulls/{number}/files?per_page=100")
    if len(items) >= 100:
        raise RuntimeError(f"PR #{number} has too many files for unpaged audit")
    return {item["filename"]: item for item in items}


def summary_pixels(left, right):
    left = left.convert("RGB")
    right = right.convert("RGB")
    size = (640, 360)
    left = ImageOps.pad(left, size, method=Image.Resampling.BICUBIC)
    right = ImageOps.pad(right, size, method=Image.Resampling.BICUBIC)
    diff = ImageChops.difference(left, right)
    hist = diff.histogram()
    changed = sum(v for i, v in enumerate(hist) if i % 256 >= 8)
    mae = sum((i % 256) * v for i, v in enumerate(hist)) / (size[0] * size[1] * 3)
    return {"channel_fraction_delta_ge_8": round(changed / (size[0] * size[1] * 3), 4),
            "mean_channel_delta": round(mae, 3)}


def draw_pair(target, before, after, idx, text=None):
    width = 1448
    h = 448
    im = Image.new("RGB", (width, h), "#ededed")
    before = ImageOps.contain(before.convert("RGB"), (704, 400))
    after = ImageOps.contain(after.convert("RGB"), (704, 400))
    im.paste(before, ((704 - before.width) // 2 + 8, 33 + (400 - before.height) // 2))
    im.paste(after, ((704 - after.width) // 2 + 734, 33 + (400 - after.height) // 2))
    draw = ImageDraw.Draw(im)
    draw.text((10, 8), "CURRENT MAIN / " + str(idx), fill="#111111")
    draw.text((734, 8), "PROPOSED PR / " + str(idx), fill="#111111")
    draw.line((724, 0, 724, h), fill="#aaaaaa", width=2)
    target.append(im)


def save_contacts(pr_number, kind, pairs):
    if not pairs:
        return []
    files = []
    for start in range(0, len(pairs), 4):
        batch = pairs[start:start+4]
        sheet = Image.new("RGB", (1448, 448 * len(batch)), "#f5f5f5")
        for pos, pair in enumerate(batch):
            sheet.paste(pair, (0, 448 * pos))
        filename = f"pr-{pr_number}-{kind}-{start+1:02d}-{start+len(batch):02d}.jpg"
        sheet.save(ROOT / filename, quality=90, optimize=True)
        files.append(filename)
    return files


def normalized(text):
    return re.sub(r"\s+", "", text)


def pdf_review(number, path, sha):
    old_bytes = Path(path).read_bytes()
    new_bytes = blob(sha)
    pairs = []
    changed_text, changed_image, page_records = [], [], []
    with fitz.open(stream=old_bytes, filetype="pdf") as a, \
         fitz.open(stream=new_bytes, filetype="pdf") as b:
        if a.page_count != b.page_count:
            raise RuntimeError(f"PDF page count changed for {path}: {a.page_count} -> {b.page_count}")
        for i in range(a.page_count):
            left_text = a[i].get_text("text", sort=True)
            right_text = b[i].get_text("text", sort=True)
            text_changed = normalized(left_text) != normalized(right_text)
            if text_changed:
                changed_text.append(i+1)
            left_pix = a[i].get_pixmap(matrix=fitz.Matrix(0.75,0.75), alpha=False)
            right_pix = b[i].get_pixmap(matrix=fitz.Matrix(0.75,0.75), alpha=False)
            left_img = Image.frombytes("RGB", (left_pix.width,left_pix.height), left_pix.samples)
            right_img = Image.frombytes("RGB", (right_pix.width,right_pix.height), right_pix.samples)
            delta = summary_pixels(left_img, right_img)
            if delta["channel_fraction_delta_ge_8"] > 0.01:
                changed_image.append(i+1)
            draw_pair(pairs, left_img, right_img, i+1)
            page_records.append({
                "page": i+1,
                "text_changed_ignoring_spaces": text_changed,
                "image": delta,
                "main_text": left_text.strip()[:1700],
                "candidate_text": right_text.strip()[:1700],
                "main_chars": len(left_text),
                "candidate_chars": len(right_text),
            })
    return {
        "path": path, "kind": "pdf",
        "pages": len(page_records), "changed_text_pages_ignoring_spaces": changed_text,
        "significant_pixel_delta_pages": changed_image,
        "per_page": page_records,
        "contact_sheets": save_contacts(number,"pdf",pairs)
    }


def pptx_review(number, path, sha):
    old = Presentation(io.BytesIO(Path(path).read_bytes()))
    new = Presentation(io.BytesIO(blob(sha)))
    if len(old.slides) != len(new.slides):
        raise RuntimeError("Slide counts differ")
    def get_shapes(slide):
        result = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                t = shape.text.strip()
                if t:
                    result.append(t)
            if shape.has_table:
                for row in shape.table.rows:
                    result.append(" | ".join(cell.text for cell in row.cells))
        return result
    records = []
    for i, (left, right) in enumerate(zip(old.slides, new.slides),1):
        ls, rs = get_shapes(left), get_shapes(right)
        records.append({
            "slide": i,
            "text_changed_ignoring_spaces": normalized("\n".join(ls)) != normalized("\n".join(rs)),
            "main_text": "\n".join(ls)[:2200],
            "candidate_text": "\n".join(rs)[:2200],
            "main_shapes": len(left.shapes),
            "candidate_shapes": len(right.shapes),
        })
    return {
        "path": path, "kind": "pptx",
        "slides": len(records),
        "text_changed_slides_ignoring_spaces": [r["slide"] for r in records if r["text_changed_ignoring_spaces"]],
        "per_slide": records,
    }


def webp_review(number, paths):
    files = changed_files(number)
    names = [path for path in paths if path in files]
    if number == 153:
        names = sorted([x for x in files if x.endswith(".webp")])
    else:
        names = sorted(names)[:6]
    images = []
    pairs = []
    for name in names:
        left_data = Path(name).read_bytes()
        right_data = blob(files[name]["sha"])
        with Image.open(io.BytesIO(left_data)) as image_a, \
             Image.open(io.BytesIO(right_data)) as image_b:
            left = image_a.convert("RGB")
            right = image_b.convert("RGB")
            detail = {
                "path": name,
                "main_dimensions": list(left.size),
                "candidate_dimensions": list(right.size),
                **summary_pixels(left, right),
            }
            images.append(detail)
            if len(pairs) < 8:
                draw_pair(pairs, left, right, name.split("/")[-1])
    contacts = save_contacts(number, "webp", pairs)
    return {"files_compared": len(images), "items": images, "contact_sheets": contacts}


def main():
    if not TOKEN:
        raise RuntimeError("GH_TOKEN required")
    ROOT.mkdir(parents=True, exist_ok=True)
    report = {"baseline": os.popen("git rev-parse HEAD").read().strip(), "reviews": []}
    for number, targets in PR_ASSETS.items():
        files = changed_files(number)
        pr = api(f"pulls/{number}")
        one = {"pr": number, "head": pr["head"]["sha"],
               "mergeable": pr.get("mergeable"), "changed_files": len(files),
               "documents": [], "webp": None}
        for path in targets:
            file = files.get(path)
            if not file or not file.get("sha") or file["status"] != "modified":
                raise RuntimeError(f"Unexpected missing or non-modified artifact #{number}: {path}")
            if path.endswith(".pdf"):
                entry = pdf_review(number, path, file["sha"])
                print(f"PR #{number} PDF {path}: {len(entry['changed_text_pages_ignoring_spaces'])}/{entry['pages']} pages text differs ignoring whitespace; significant image changes {len(entry['significant_pixel_delta_pages'])}",flush=True)
            else:
                entry = pptx_review(number, path, file["sha"])
                print(f"PR #{number} PPTX {path}: {len(entry['text_changed_slides_ignoring_spaces'])}/{entry['slides']} slides differ ignoring whitespace", flush=True)
            one["documents"].append(entry)
        preview_paths = [name for name in files if name.endswith(".webp")]
        if preview_paths:
            one["webp"] = webp_review(number, preview_paths)
            d = one["webp"]["items"]
            print(f"PR #{number} WebP compared {len(d)}; size changes {sum(x['main_dimensions'] != x['candidate_dimensions'] for x in d)}; >0.01 pixel-fraction changes {sum(x['channel_fraction_delta_ge_8']>0.01 for x in d)}", flush=True)
        report["reviews"].append(one)
    (ROOT/"comparison.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("PASS read-only visual evidence exported; no refs/files modified.",flush=True)


if __name__=="__main__":
    main()
