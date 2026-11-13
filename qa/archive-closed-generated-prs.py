#!/usr/bin/env python3
"""Archive explicitly reviewed, closed generated PR heads before branch cleanup.

This reads a fixed manifest; it never discovers candidates for deletion.
Run --verify-only without write permission in PRs, --archive only after merge.
"Superseded" means the newer open PR covers every changed path, *not*
byte equality or visual equivalence. The old commit stays reachable by tag.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = os.getenv("GITHUB_REPOSITORY", "dohyunkimmm/mosigo-case-study")
TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
MANIFEST = Path("qa/closed-generated-prs-manifest.json")
TAG_ROOT = "archive/closed/20261114"


def request(method: str, endpoint: str, body: dict | None = None, missing_ok: bool = False):
    if not TOKEN:
        raise RuntimeError("GH_TOKEN is required")
    url = "https://api.github.com/repos/" + REPO + "/" + endpoint
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": "Bearer " + TOKEN,
            "Accept": "application/vnd.github+json",
            "User-Agent": "mosigo-reviewed-generated-pr-archive",
        },
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                data = response.read()
                return json.loads(data) if data else {}
        except urllib.error.HTTPError as e:
            if e.code == 404 and missing_ok:
                return None
            if e.code < 500 or attempt == 3:
                raise RuntimeError(f"{method} {endpoint}: HTTP {e.code} {e.read()[:200]!r}") from e
        except urllib.error.URLError:
            if attempt == 3:
                raise
        time.sleep(2 ** attempt)


def get(endpoint, missing_ok=False):
    return request("GET", endpoint, missing_ok=missing_ok)


def changed_files(number: int):
    files = get(f"pulls/{number}/files?per_page=100")
    if not isinstance(files, list) or len(files) >= 100:
        raise RuntimeError(f"Files list incomplete for PR #{number}")
    return files


def head_ref(name):
    result = get("git/ref/heads/" + name, missing_ok=True)
    return result["object"]["sha"] if result else None


def tag_ref(name):
    result = get("git/ref/tags/" + name, missing_ok=True)
    return result["object"]["sha"] if result else None


def validate():
    entries = json.loads(MANIFEST.read_text())
    if not isinstance(entries, list) or not entries or len(entries) > 50:
        raise ValueError("A nonempty 1..50 item reviewed manifest is required")
    open_prs = get("pulls?state=open&per_page=100")
    if not isinstance(open_prs, list) or len(open_prs) >= 100:
        raise RuntimeError("Cannot prove no other open PR uses a head branch")

    seen_numbers, seen_branches = set(), set()
    verified = []
    newer_cache = {}
    for entry in entries:
        number, name, sha, successor = (
            entry["number"], entry["branch"], entry["sha"], entry["superseded_by"]
        )
        if not isinstance(number, int) or not isinstance(successor, int):
            raise ValueError("PR numbers must be integers")
        if number in seen_numbers or name in seen_branches or successor <= number:
            raise ValueError("Duplicate or non-newer PR in manifest")
        seen_numbers.add(number)
        seen_branches.add(name)
        if not re.fullmatch(r"automation/[a-z0-9][A-Za-z0-9._/-]*", name) or ".." in name:
            raise ValueError("Not a safe generated branch")
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError("Expected SHA must be exactly 40 hexadecimal characters")

        pr = get(f"pulls/{number}")
        if not (
            pr["state"] == "closed" and not pr["merged"]
            and pr["base"]["ref"] == "main"
            and pr["head"]["ref"] == name
            and pr["head"]["sha"] == sha
            and pr["head"]["repo"]["full_name"] == REPO
        ):
            raise RuntimeError(f"PR #{number} is not the exact reviewed closed head")
        if any(p["head"]["ref"] == name and p["head"]["repo"]["full_name"] == REPO
               for p in open_prs):
            raise RuntimeError(f"Head {name} is still in use by an open PR")

        if successor not in newer_cache:
            newer = get(f"pulls/{successor}")
            if not (
                newer["state"] == "open" and newer["head"]["repo"]["full_name"] == REPO
                and newer["head"]["ref"].startswith("automation/")
            ):
                raise RuntimeError(f"Superseding PR #{successor} must still be open")
            newer_cache[successor] = (
                newer["head"]["ref"],
                {file["filename"] for file in changed_files(successor)}
            )
        successor_branch, successor_paths = newer_cache[successor]
        kind = name.split("/")[1].split("-")[0]
        # Avoid cross-kind successor mistakes (ppt-preview vs mobile-previews).
        if not (name.split("/")[1].split("-", 2)[:2] ==
                successor_branch.split("/")[1].split("-", 2)[:2]):
            raise RuntimeError(f"PR #{number} and #{successor} are different generators")
        before = changed_files(number)
        if not before or any(f["status"] != "modified" for f in before):
            raise RuntimeError(f"PR #{number} has non-modified file types")
        missing_paths = sorted({file["filename"] for file in before} - successor_paths)
        if missing_paths:
            raise RuntimeError(f"PR #{successor} doesn't cover all of #{number}: {missing_paths}")

        current = head_ref(name)
        archive_name = f"{TAG_ROOT}/pr-{number}/{name}"
        tagged = tag_ref(archive_name)
        if current not in (None, sha):
            raise RuntimeError(f"Branch {name} moved: {current} != {sha}")
        if tagged not in (None, sha):
            raise RuntimeError(f"Archive tag conflicts for #{number}: {tagged}")
        if current is None and tagged is None:
            raise RuntimeError(f"Neither branch nor archive tag exists for #{number}")
        verified.append({"number": number, "branch": name, "sha": sha,
                         "archive": archive_name, "successor": successor,
                         "changed_paths": len(before), "branch_present": current is not None})
    return verified


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--verify-only"
    if mode not in ("--verify-only", "--archive"):
        raise ValueError("Supported modes: --verify-only, --archive")
    entries = validate()  # Do not make any mutations until every manifest item passes.
    print(f"PASS reviewed manifest: {len(entries)} closed heads, successors cover every changed path",
          flush=True)
    for e in entries:
        print(f"#{e['number']} -> #{e['successor']}: {e['changed_paths']} paths,"
              f" original={e['sha']}, archive={e['archive']}", flush=True)
    if mode == "--verify-only":
        print("Read-only verification complete; no Git references modified.", flush=True)
        return

    # Phase 1: Preserve all exact commit SHAs as immutable-to-this-script tags.
    for e in entries:
        if tag_ref(e["archive"]) is None:
            request("POST", "git/refs",
                    {"ref": "refs/tags/" + e["archive"], "sha": e["sha"]})
        if tag_ref(e["archive"]) != e["sha"]:
            raise RuntimeError(f"Archive tag readback failed: #{e['number']}")
    print("PASS every exact SHA is stored as a verified Git tag", flush=True)

    # Phase 2: Remove only heads that still equal their reviewed commit.
    for e in entries:
        current = head_ref(e["branch"])
        if current is None:
            continue
        if current != e["sha"] or tag_ref(e["archive"]) != e["sha"]:
            raise RuntimeError(f"Head or archive moved during cleanup: #{e['number']}")
        request("DELETE", "git/refs/heads/" + e["branch"])
        if head_ref(e["branch"]) is not None:
            raise RuntimeError(f"Branch was not removed: #{e['number']}")
        print(f"PASS safely retired branch for #{e['number']}", flush=True)

    print("PASS archived all manifest commits and retired their closed branches", flush=True)


if __name__ == "__main__":
    main()
