#!/usr/bin/env python3
"""Preserve exact HEADs of four reviewed, closed generated PRs before ref cleanup.

Only the four hard-coded, reviewed branches may be removed; the integrated
deliverables must already be merged and identical to main's Git blobs. No
guessing about the byte/visual equivalence of superseded PRs is made.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "dohyunkimmm/mosigo-case-study")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
MAIN_MERGE = "2144de61b578d769102798d85dd220dee4ffe5df"
SUCCEEDED_BY = 178
TAG_ROOT = "archive/closed/20261114"
TARGETS = (
    (135, "automation/ir-deck-43244522333-1", "e4bd40e710c114a68fd24b8e3f84c3a9fe04efba"),
    (139, "automation/business-plan-43246431581-1", "7938a929a3a4aa0f0ec7480999d28dc35e82bcce"),
    (153, "automation/mobile-previews-43356411195-1", "21577fa8be8ae8d3aeca4de7b715170c30e44b77"),
    (154, "automation/ppt-preview-43356411319-1", "109bed4160f6b32be0b7bfc2604d5e83f311ed1b"),
)


def request(method, path, body=None, missing_ok=False):
    if not TOKEN or REPO != "dohyunkimmm/mosigo-case-study":
        raise RuntimeError("Expected GH_TOKEN and canonical repository")
    r = urllib.request.Request(
        "https://api.github.com/repos/" + REPO + "/" + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Authorization": "Bearer " + TOKEN, "Accept": "application/vnd.github+json",
                 "User-Agent": "mosigo-final-four-archive"},
    )
    for n in range(4):
        try:
            with urllib.request.urlopen(r, timeout=45) as response:
                raw = response.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            if exc.code == 404 and missing_ok:
                return None
            if exc.code < 500 or n == 3:
                raise RuntimeError(f"{method} {path} failed: {exc.code} {exc.read()[:200]!r}") from exc
        except urllib.error.URLError:
            if n == 3:
                raise
        time.sleep(2 ** n)


def get(path, missing_ok=False):
    return request("GET", path, missing_ok=missing_ok)


def branch_sha(name):
    ref = get("git/ref/heads/" + name, missing_ok=True)
    return ref["object"]["sha"] if ref is not None else None


def archived_sha(tag):
    # The /git/ref/ endpoint has prefix-matching behavior: require full
    # exact ref comparison instead of using an ambiguous returned object.
    refs = get("git/matching-refs/tags/" + tag)
    if not isinstance(refs, list):
        raise RuntimeError("Expected matching-ref array")
    matches = [x for x in refs if x.get("ref") == "refs/tags/" + tag]
    if len(matches) > 1:
        raise RuntimeError("Conflicting duplicate tag refs")
    return matches[0]["object"]["sha"] if matches else None


def all_pr_files(number):
    items = get(f"pulls/{number}/files?per_page=100")
    if not isinstance(items, list) or len(items) >= 100:
        raise RuntimeError(f"PR #{number} changed paths incomplete")
    return items


def validate():
    successor = get(f"pulls/{SUCCEEDED_BY}")
    if not successor.get("merged") or successor.get("merge_commit_sha") != MAIN_MERGE:
        raise RuntimeError("Final reviewed PR #178 was not merged at the expected SHA")
    integrated_files = {x["filename"]: x["sha"] for x in all_pr_files(SUCCEEDED_BY)}
    main_tree = get("git/trees/main?recursive=1")
    if main_tree.get("truncated"):
        raise RuntimeError("Cannot validate complete main tree")
    main_paths = {x["path"]: x["sha"] for x in main_tree["tree"] if x["type"] == "blob"}
    if not integrated_files:
        raise RuntimeError("Final PR has no files")
    for name, sha in integrated_files.items():
        if main_paths.get(name) != sha:
            raise RuntimeError(f"Current main no longer contains final reviewed artifact {name}")

    pending = get("pulls?state=open&per_page=100")
    if not isinstance(pending, list) or len(pending) >= 100:
        raise RuntimeError("Open PR listing incomplete")

    results = []
    for number, branch, sha in TARGETS:
        if not branch.startswith("automation/") or ".." in branch or not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise RuntimeError("Unexpected hardcoded branch or commit SHA")
        pr = get(f"pulls/{number}")
        if not (pr["state"] == "closed" and pr["merged"] is False
                and pr["head"]["sha"] == sha and pr["head"]["ref"] == branch
                and pr["head"]["repo"]["full_name"] == REPO and pr["base"]["ref"] == "main"):
            raise RuntimeError(f"Original PR #{number} metadata changed")
        if any(item["head"]["ref"] == branch for item in pending):
            raise RuntimeError(f"Source branch still used by an open PR: {branch}")
        original = all_pr_files(number)
        if not original or any(f["status"] != "modified" for f in original):
            raise RuntimeError(f"Original PR #{number} contains additions/removals")
        uncovered = sorted({item["filename"] for item in original} - integrated_files.keys())
        if uncovered:
            raise RuntimeError(f"PR #{number} changed files not included in #178: {uncovered}")
        tag = f"{TAG_ROOT}/pr-{number}/{branch}"
        actual_head, saved_sha = branch_sha(branch), archived_sha(tag)
        if actual_head not in (None, sha) or saved_sha not in (None, sha):
            raise RuntimeError(f"Unexpected/moved original ref for PR #{number}")
        if actual_head is None and saved_sha is None:
            raise RuntimeError(f"No reachable source commit for PR #{number}")
        results.append((number, branch, sha, tag, len(original)))
    return results


def main():
    mode = sys.argv[1] if len(sys.argv) == 2 else "--verify-only"
    if mode not in ("--verify-only", "--archive"):
        raise ValueError("Expected --verify-only or --archive")
    rows = validate()
    for number, _branch, sha, _tag, count in rows:
        print(f"PASS closed PR #{number}: head {sha}, {count} paths preserved by reviewed #178", flush=True)
    if mode == "--verify-only":
        print("PASS checked all four original PR heads; no refs changed", flush=True)
        return
    # All validation happens before any write. Preserve *every* original SHA first.
    for number, branch, sha, tag, _count in rows:
        if archived_sha(tag) is None:
            request("POST", "git/refs", {"ref": "refs/tags/" + tag, "sha": sha})
        if archived_sha(tag) != sha:
            raise RuntimeError(f"Tag SHA verification failed for #{number}")
        print(f"PASS archived PR #{number} as {tag}", flush=True)
    # Never delete a branch unless the reviewed tag and current ref both match.
    for number, branch, sha, tag, _count in rows:
        head = branch_sha(branch)
        if head is None:
            continue
        if head != sha or archived_sha(tag) != sha:
            raise RuntimeError(f"PR #{number}: branch or tag changed during audit")
        request("DELETE", "git/refs/heads/" + branch)
        if branch_sha(branch) is not None:
            raise RuntimeError(f"PR #{number} branch still exists after deletion")
        print(f"PASS retired exact reviewed PR #{number} branch", flush=True)
    print("PASS all four old commits tagged; old branches safely retired", flush=True)


if __name__ == "__main__":
    main()
