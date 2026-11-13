#!/usr/bin/env bash
# Publish generated assets for review; never push generated files directly to main.
set -euo pipefail

kind="${1:?generator identifier required}"
title="${2:?commit title required}"
shift 2
test "$#" -gt 0 || { echo "::error::No generated paths specified"; exit 1; }
[[ "$kind" =~ ^[a-z][a-z0-9-]*$ ]] || { echo "::error::Invalid generator identifier"; exit 1; }

# A PR checkout must never write to a head branch or an untrusted fork.
if [[ "${GITHUB_REF:-}" != "refs/heads/main" ]] ||
   [[ "${GITHUB_EVENT_NAME:-}" != "push" && "${GITHUB_EVENT_NAME:-}" != "workflow_dispatch" ]]; then
  echo "Not publishing: only trusted main pushes or main manual runs open generated PRs."
  exit 0
fi

: "${GITHUB_REPOSITORY:?GitHub repository required}"
: "${GITHUB_RUN_ID:?GitHub run ID required}"
: "${GITHUB_RUN_ATTEMPT:?GitHub run attempt required}"
: "${GH_TOKEN:?Workflow PR write token required}"

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add -A -- "$@"
if git diff --cached --quiet; then
  echo "Generated assets are already synchronized; no PR required."
  exit 0
fi

# Only one outstanding review per generator. Avoid producing an unbounded queue
# of conflicting binary PRs while keeping every new render in the workflow's
# uploaded artifact. Do not replace an existing PR's reviewed bytes.
open_prs="$(gh api "repos/${GITHUB_REPOSITORY}/pulls?state=open&per_page=100")"
open_count="$(jq 'length' <<< "$open_prs")"
if (( open_count >= 100 )); then
  echo "::error::Cannot safely check all open PRs with a single page; manual review required."
  exit 1
fi
existing="$(jq -r --arg repo "$GITHUB_REPOSITORY" --arg prefix "automation/${kind}-" '
  [.[] | select(.base.ref == "main" and .head.repo.full_name == $repo and
       (.head.ref | startswith($prefix))) | .number] | join(", ")
' <<< "$open_prs")"
if [[ -n "$existing" ]]; then
  echo "::warning::Generated ${kind} assets differ from main but PR(s) #${existing} still await review. Not opening another conflicting PR. Inspect this run's uploaded artifact; resolve previous PRs first."
  if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    {
      echo "### Generated ${kind} assets need review"
      echo "New output differs from main, but existing PR(s) **#${existing}** for this generator are open."
      echo "A new PR was **not** opened to avoid parallel conflicting binary reviews."
      echo "Inspect this workflow run's generated artifact, then resolve the older PR before publishing a new candidate."
    } >> "$GITHUB_STEP_SUMMARY"
  fi
  exit 0
fi

branch="automation/${kind}-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"
git commit -m "$title"
git push origin "HEAD:refs/heads/${branch}"

body="Generated artifacts from GitHub Actions run ${GITHUB_RUN_ID} (attempt ${GITHUB_RUN_ATTEMPT}).

Source workflow: ${GITHUB_WORKFLOW:-unknown}. Please review the generated files and wait for both required QA checks before merging. Bot-created pull-request checks may require a repository writer to approve workflow runs.

This automation never pushes directly to main and never auto-merges a PR."
if ! gh pr create --repo "$GITHUB_REPOSITORY" --base main --head "$branch" --title "$title" --body "$body"; then
  echo "::error::Failed to open generated PR. Enable Settings > Actions > General > Allow GitHub Actions to create and approve pull requests, then retry."
  exit 1
fi
