"""Wait for the latest GitHub Actions workflow run to complete."""
import os
import sys
import time
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER = os.environ.get("GITHUB_OWNER", "")
REPO = os.environ.get("GITHUB_REPO", "")
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}
BASE = f"https://api.github.com/repos/{OWNER}/{REPO}"


def wait_for_latest_run(name_filter=None, timeout=600, initial_sleep=15):
    print(f"Aguardando workflow '{name_filter or 'qualquer'}' iniciar (sleep {initial_sleep}s)...")
    time.sleep(initial_sleep)

    for attempt in range(timeout // 15):
        r = requests.get(f"{BASE}/actions/runs", headers=HEADERS, params={"per_page": 10})
        r.raise_for_status()
        runs = r.json().get("workflow_runs", [])

        if name_filter:
            runs = [x for x in runs if x.get("name", "") == name_filter]

        if not runs:
            print(f"  Nenhum run encontrado. Tentativa {attempt+1}...")
            time.sleep(15)
            continue

        run = runs[0]
        status = run["status"]
        run_id = run["id"]
        conclusion = run.get("conclusion") or "..."
        name = run.get("name", "?")
        print(f"  [{attempt+1}] Run {run_id} ({name}) - {status} - {conclusion}")

        if status == "completed":
            print(f"  Concluido: {conclusion.upper()}")
            return run_id, conclusion

        time.sleep(15)

    print("  TIMEOUT aguardando workflow")
    return None, "timeout"


if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: GITHUB_TOKEN not set")
        sys.exit(1)
    name = sys.argv[1] if len(sys.argv) > 1 else "CI Sequential"
    run_id, conclusion = wait_for_latest_run(name_filter=name)
    print(f"RUN_ID={run_id} CONCLUSION={conclusion}")
