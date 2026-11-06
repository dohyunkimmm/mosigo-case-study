#!/usr/bin/env bash
# Vercel: exit 0 to skip, exit 1 to build.
# Preserve every Preview; skip Production only when a commit changes
# repository administration files and internal QA Markdown, not site assets.
set -u

if [ "${VERCEL_ENV:-}" != "production" ]; then
  echo "Build: preview or unknown environment (fail open)."
  exit 1
fi

# Vercel's Git clone may be shallow. Never skip if the diff is unavailable.
if ! git rev-parse --verify 'HEAD^' >/dev/null 2>&1; then
  echo "Build: parent commit unavailable (fail open)."
  exit 1
fi

if ! changed="$(git diff --name-only --no-renames HEAD^ HEAD --)"; then
  echo "Build: cannot determine changed files (fail open)."
  exit 1
fi
if [ -z "$changed" ]; then
  echo "Build: no changed files reported (fail open)."
  exit 1
fi

while IFS= read -r path; do
  case "$path" in
    README.md|.github/workflows/*|qa/*.md)
      ;;
    *)
      echo "Build: deployable or unclassified file changed: $path"
      exit 1
      ;;
  esac
done <<< "$changed"

echo "Skip: production commit changes only internal repository/QA documentation."
exit 0
