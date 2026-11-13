#!/usr/bin/env python3
"""Offline regression checks for generated-asset PR publication safety."""
import json
import os
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
PUBLISH = ROOT / ".github/scripts/publish-generated-pr.sh"

with tempfile.TemporaryDirectory() as root:
    root = pathlib.Path(root)
    bin_dir = root / "bin"
    bin_dir.mkdir()
    log = root / "actions.log"
    fake_git = bin_dir / "git"
    fake_git.write_text("""#!/usr/bin/env bash
printf 'git %s\\n' "$*" >> "$MOCK_ACTIONS"
if [[ "$1" == diff && "$2" == --cached && "$3" == --quiet ]]; then
  [[ "$MOCK_CHANGED" == 0 ]] && exit 0
  exit 1
fi
exit 0
""")
    fake_gh = bin_dir / "gh"
    fake_gh.write_text("""#!/usr/bin/env bash
printf 'gh %s\\n' "$*" >> "$MOCK_ACTIONS"
if [[ "$1" == api ]]; then cat "$MOCK_PRS"; exit 0; fi
if [[ "$1" == pr && "$2" == create ]]; then exit 0; fi
exit 3
""")
    fake_git.chmod(0o755)
    fake_gh.chmod(0o755)

    def run_case(name, open_prs, changed=True, event="push", ref="refs/heads/main", expected=0):
        mock_prs = root / "prs.json"
        mock_prs.write_text(json.dumps(open_prs))
        log.write_text("")
        summary = root / "summary.md"
        summary.write_text("")
        env = dict(os.environ)
        env.update({
            "PATH": str(bin_dir) + os.pathsep + env["PATH"],
            "GH_TOKEN": "offline-test-token",
            "GITHUB_REF": ref,
            "GITHUB_EVENT_NAME": event,
            "GITHUB_REPOSITORY": "dohyunkimmm/mosigo-case-study",
            "GITHUB_RUN_ID": "12345678",
            "GITHUB_RUN_ATTEMPT": "1",
            "GITHUB_WORKFLOW": "Offline unit test",
            "GITHUB_STEP_SUMMARY": str(summary),
            "MOCK_ACTIONS": str(log),
            "MOCK_PRS": str(mock_prs),
            "MOCK_CHANGED": "1" if changed else "0",
        })
        completed = subprocess.run(
            ["bash", str(PUBLISH), "mobile-previews", "Generated preview", "downloads/previews/plan-01.webp"],
            cwd=root, env=env, capture_output=True, text=True, check=False,
        )
        assert completed.returncode == expected, (name, completed.stdout, completed.stderr)
        return log.read_text(), summary.read_text(), completed.stdout + completed.stderr

    pending = [{
        "number": 129,
        "base": {"ref": "main"},
        "head": {"ref": "automation/mobile-previews-43242430205-1", "repo": {"full_name": "dohyunkimmm/mosigo-case-study"}}
    }]
    actions, summary, output = run_case("already pending", pending)
    assert "gh api repos/dohyunkimmm/mosigo-case-study/pulls" in actions
    assert "git commit" not in actions and "git push" not in actions and "gh pr create" not in actions
    assert "#129" in summary and "conflicting PR" in output

    actions, summary, output = run_case("first review", [])
    assert "git commit -m Generated preview" in actions
    assert "git push origin HEAD:refs/heads/automation/mobile-previews-12345678-1" in actions
    assert "gh pr create" in actions

    actions, _, output = run_case("no change", [], changed=False)
    assert "gh api" not in actions and "git commit" not in actions
    assert "already synchronized" in output

    actions, _, output = run_case("untrusted PR context", [], ref="refs/pull/2/merge", event="pull_request")
    assert actions == "" and "Not publishing" in output

    actions, _, output = run_case("refuse truncated PR list", pending * 100, expected=1)
    assert "git commit" not in actions and "gh pr create" not in actions
    assert "Cannot safely check all open PRs" in output

print("PASS generated artifact PR backlog guard: 5 independent scenarios")
