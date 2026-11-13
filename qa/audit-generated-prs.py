#!/usr/bin/env python3
"""Read-only semantic audit of open generated PR deliverables against main.

Conservative classifications: equivalence requires same decoded WebP pixels,
same PDF text AND rendered pixels, or identical nonvolatile PPTX parts.
Any error, addition, removal or unsupported file prevents auto-retirement.
This script never changes a branch, PR, tag or published artifact.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from functools import lru_cache
from pathlib import Path

from PIL import Image
import fitz

REPO = os.environ.get("GITHUB_REPOSITORY", "dohyunkimmm/mosigo-case-study")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
API = "https://api.github.com/repos/" + REPO
OUT = Path("qa-artifacts/generated-pr-audit.json")


def api(path: str) -> dict | list:
    req = urllib.request.Request(
        "https://api.github.com/" + path.lstrip("/"),
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "mosigo-case-study-generated-pr-audit",
            **({"Authorization": "Bearer " + TOKEN} if TOKEN else {}),
        },
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=50) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("unreachable")


@lru_cache(maxsize=4096)
def blob(sha: str) -> bytes:
    payload = api(f"repos/{REPO}/git/blobs/{sha}")
    if payload.get("encoding") != "base64":
        raise RuntimeError(f"unsupported blob encoding for {sha}")
    return base64.b64decode(payload["content"])


def hash_parts(parts: list[bytes]) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(len(part).to_bytes(8, "big"))
        digest.update(part)
    return digest.hexdigest()


@lru_cache(maxsize=4096)
def fingerprint(sha: str, suffix: str) -> str:
    data = blob(sha)
    if suffix == ".webp":
        with Image.open(io.BytesIO(data)) as image:
            rgba = image.convert("RGBA")
            return hash_parts([
                str(rgba.size).encode(), rgba.tobytes()
            ])
    if suffix == ".pdf":
        items: list[bytes] = []
        with fitz.open(stream=data, filetype="pdf") as document:
            items.append(str(document.page_count).encode())
            for page in document:
                items.append(page.get_text("text", sort=True).encode("utf-8"))
                pixmap = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
                items.extend([
                    str((pixmap.width, pixmap.height)).encode(),
                    pixmap.samples,
                ])
        return hash_parts(items)
    if suffix == ".pptx":
        with zipfile.ZipFile(io.BytesIO(data)) as document:
            names = sorted(
                name for name in document.namelist()
                if not name.endswith("/")
                and name not in {"docProps/core.xml", "docProps/app.xml"}
            )
            return hash_parts([
                item for name in names
                for item in (name.encode("utf-8"), document.read(name))
            ])
    raise RuntimeError("unsupported semantic format: " + suffix)


def all_pages(path: str) -> list:
    entries = []
    for page in range(1, 20):
        separator = "&" if "?" in path else "?"
        batch = api(path + separator + f"per_page=100&page={page}")
        if not isinstance(batch, list):
            raise RuntimeError("list response missing for " + path)
        entries.extend(batch)
        if len(batch) < 100:
            return entries
    raise RuntimeError("pagination exceeded for " + path)


def main() -> int:
    if not TOKEN:
        print("GitHub token is required", file=sys.stderr)
        return 2
    tree = api(f"repos/{REPO}/git/trees/main?recursive=1")
    if tree.get("truncated"):
        raise RuntimeError("main tree truncated; cannot audit safely")
    main_blobs = {
        item["path"]: item["sha"]
        for item in tree["tree"] if item["type"] == "blob"
    }
    open_prs = all_pages(f"repos/{REPO}/pulls?state=open")
    generated = sorted(
        (pr for pr in open_prs
         if pr["head"]["ref"].startswith("automation/")
         and pr["head"]["repo"]["full_name"] == REPO),
        key=lambda pr: pr["number"],
    )
    report = {
        "repository": REPO,
        "main_sha": tree["sha"],
        "generated_prs": len(generated),
        "comparisons": [],
        "criteria": {
            "webp": "same decoded width, height and RGBA pixels",
            "pdf": "same page count, extracted text and rendered RGB pixels",
            "pptx": "same OOXML parts excluding volatile docProps metadata",
            "unsupported": "never classified as equivalent",
        },
    }
    safe = []
    for pr in generated:
        files = all_pages(f"repos/{REPO}/pulls/{pr['number']}/files")
        finding = {
            "number": pr["number"],
            "branch": pr["head"]["ref"],
            "head_sha": pr["head"]["sha"],
            "files": len(files),
            "equivalent_files": 0,
            "different": [],
            "errors": [],
        }
        for file in files:
            path = file["filename"]
            head_sha = file.get("sha")
            base_sha = main_blobs.get(path)
            if not head_sha or not base_sha or file["status"] != "modified":
                finding["different"].append({"path": path, "reason": "added, deleted or unknown"})
                continue
            if head_sha == base_sha:
                finding["equivalent_files"] += 1
                continue
            suffix = Path(path).suffix.lower()
            if suffix not in {".webp", ".pdf", ".pptx"}:
                finding["different"].append({"path": path, "reason": "unsupported file type"})
                continue
            try:
                current_signature = fingerprint(base_sha, suffix)
                proposed_signature = fingerprint(head_sha, suffix)
                if current_signature == proposed_signature:
                    finding["equivalent_files"] += 1
                else:
                    finding["different"].append({"path": path, "reason": "decoded or document content differs"})
            except Exception as exc:
                finding["errors"].append({"path": path, "error": str(exc)[:240]})
        finding["semantic_equivalent"] = (
            bool(files)
            and len(files) == finding["equivalent_files"]
            and not finding["different"]
            and not finding["errors"]
        )
        if finding["semantic_equivalent"]:
            safe.append(pr["number"])
        report["comparisons"].append(finding)
        print(
            f"PR #{pr['number']}: {finding['equivalent_files']}/{len(files)} semantically equal,"
            f" differences={len(finding['different'])}, errors={len(finding['errors'])},"
            f" safe-to-close={finding['semantic_equivalent']}",
            flush=True,
        )
    report["safe_to_retire_candidates"] = safe
    report["not_equivalent_or_unverified"] = [
        x["number"] for x in report["comparisons"] if not x["semantic_equivalent"]
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Audit complete. Candidate redundant PRs: {safe}", flush=True)
    print(f"Audit JSON: {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
