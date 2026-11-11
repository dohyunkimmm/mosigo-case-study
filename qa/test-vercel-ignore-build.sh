#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
script="$script_dir/vercel-ignore-build.sh"
repo="$(mktemp -d)"
trap 'rm -rf "$repo"' EXIT

git -C "$repo" init -q -b main
git -C "$repo" config user.email "test@example.invalid"
git -C "$repo" config user.name "Test"

commit_change() {
  local path="$1" value="$2"
  mkdir -p "$repo/$(dirname "$path")"
  printf '%s\n' "$value" > "$repo/$path"
  git -C "$repo" add -A
  git -C "$repo" commit -qm "test: $path"
}

assert_exit() {
  local expected="$1" env="$2" desc="$3"
  local actual
  set +e
  (cd "$repo" && VERCEL_ENV="$env" bash "$script" >/dev/null)
  actual=$?
  set -e
  if [ "$actual" -ne "$expected" ]; then
    printf 'FAIL %s: expected %s, got %s\n' "$desc" "$expected" "$actual" >&2
    exit 1
  fi
  printf 'PASS %s\n' "$desc"
}

commit_change index.html '<h1>initial</h1>'
assert_exit 1 production 'no parent fails open'
commit_change README.md 'internal note'
assert_exit 0 production 'README-only production skipped'
# An explicit reviewer-approved release marker forces a docs-only build.
git -C "$repo" commit --amend -qm 'ci: publish verified main [force deploy]'
assert_exit 1 production 'force-deploy marker triggers production build'
commit_change README.md 'internal note after forced deploy'
assert_exit 0 production 'ordinary docs-only skip preserved'
assert_exit 1 preview 'README-only preview still deployed'
assert_exit 1 '' 'unknown environment fails open'
commit_change index.html '<h1>updated</h1>'
assert_exit 1 production 'site changes deployed'
commit_change qa/notes/audit.md 'internal review'
assert_exit 0 production 'internal QA Markdown skipped'
commit_change downloads/report.pdf 'new artifact'
assert_exit 1 production 'downloaded assets deployed'
commit_change .github/workflows/verify.yml 'name: checks'
assert_exit 0 production 'workflow-only production skipped'
commit_change .github/scripts/publish-generated-pr.sh 'echo test'
assert_exit 0 production 'workflow-helper-only production skipped'
commit_change .gitignore 'tmp/'
assert_exit 1 production 'unclassified files deployed'
printf 'PASS all ignore-build checks\n'
