"""Collect CI/CD metrics from GitHub Actions API and save to data/."""
import csv
import json
import os
import sys
import time
import zipfile
import io
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("ERROR: 'requests' not installed. Run: pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_OWNER = os.environ.get("GITHUB_OWNER", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

BASE_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"


def _get(url: str, params: dict = None) -> dict:
    """GET with retry on 429 rate-limit."""
    for attempt in range(3):
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 60))
            print(f"  Rate limited. Waiting {retry_after}s …")
            time.sleep(retry_after)
            continue
        resp.raise_for_status()
        return resp
    raise RuntimeError(f"Failed to GET {url} after retries.")


def _paginate(url: str, params: dict = None) -> list:
    """Collect all pages of a GitHub API list endpoint."""
    if params is None:
        params = {}
    params["per_page"] = 100
    results = []
    page = 1
    while True:
        params["page"] = page
        resp = _get(url, params)
        data = resp.json()

        # Unwrap wrapper objects like {"workflow_runs": [...]}
        if isinstance(data, dict):
            for key in ("workflow_runs", "jobs", "artifacts"):
                if key in data:
                    data = data[key]
                    break

        if not data:
            break
        results.extend(data)

        # Check Link header for next page
        link_header = resp.headers.get("Link", "")
        if 'rel="next"' not in link_header:
            break
        page += 1
    return results


def _duration_seconds(started: str, completed: str) -> float:
    """Return duration in seconds between two ISO timestamps."""
    if not started or not completed:
        return 0.0
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    try:
        t0 = datetime.strptime(started, fmt).replace(tzinfo=timezone.utc)
        t1 = datetime.strptime(completed, fmt).replace(tzinfo=timezone.utc)
        return max(0.0, (t1 - t0).total_seconds())
    except ValueError:
        return 0.0


def _fetch_test_results(run_id: int) -> dict:
    """Try to download test-results artifact and parse junit XML."""
    defaults = {
        "test_count": None,
        "test_failures": None,
        "test_errors": None,
        "test_duration_total": None,
    }
    try:
        artifacts = _get(f"{BASE_URL}/actions/runs/{run_id}/artifacts").json()
        artifact_list = artifacts.get("artifacts", [])
        target = next(
            (a for a in artifact_list if "test-results" in a["name"].lower()),
            None,
        )
        if not target:
            return defaults

        dl_url = target["archive_download_url"]
        resp = requests.get(dl_url, headers=HEADERS, timeout=60)
        resp.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            xml_names = [n for n in zf.namelist() if n.endswith(".xml")]
            if not xml_names:
                return defaults
            xml_content = zf.read(xml_names[0]).decode("utf-8")

        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_content)

        suite = root if root.tag == "testsuite" else root.find("testsuite")
        if suite is None:
            return defaults

        return {
            "test_count": int(suite.get("tests", 0)),
            "test_failures": int(suite.get("failures", 0)),
            "test_errors": int(suite.get("errors", 0)),
            "test_duration_total": float(suite.get("time", 0.0)),
        }
    except Exception as exc:
        print(f"  Warning: could not fetch test results for run {run_id}: {exc}")
        return defaults


def collect() -> None:
    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN not set.")
        sys.exit(1)
    if not GITHUB_OWNER or not GITHUB_REPO:
        print("ERROR: GITHUB_OWNER and GITHUB_REPO must be set.")
        sys.exit(1)

    os.makedirs(DATA_DIR, exist_ok=True)

    print(f"Fetching workflow runs for {GITHUB_OWNER}/{GITHUB_REPO} …")
    runs = _paginate(f"{BASE_URL}/actions/runs")
    print(f"  Found {len(runs)} runs total.")

    metrics_rows = []
    steps_rows = []

    for run in runs:
        run_id = run["id"]
        sha = run.get("head_sha", "")[:8]
        commit_msg = (run.get("head_commit") or {}).get("message", "")
        commit_msg = commit_msg.splitlines()[0] if commit_msg else ""
        status = run.get("conclusion") or run.get("status", "unknown")
        workflow_name = run.get("name", "unknown")
        timestamp = run.get("created_at", "")
        w_duration = _duration_seconds(
            run.get("created_at", ""), run.get("updated_at", "")
        )

        print(f"  Processing run {run_id} ({workflow_name}) [{status}] …")

        # Fetch jobs
        jobs_data = _get(
            f"{BASE_URL}/actions/runs/{run_id}/jobs"
        ).json().get("jobs", [])

        # Fetch test results once per run
        test_info = _fetch_test_results(run_id)

        if not jobs_data:
            metrics_rows.append({
                "run_id": run_id,
                "commit_sha": sha,
                "commit_message": commit_msg,
                "workflow_name": workflow_name,
                "status": status,
                "workflow_duration": w_duration,
                "job_name": "",
                "job_duration": 0,
                **test_info,
                "timestamp": timestamp,
            })
            continue

        for job in jobs_data:
            job_name = job.get("name", "")
            j_duration = _duration_seconds(
                job.get("started_at", ""), job.get("completed_at", "")
            )

            metrics_rows.append({
                "run_id": run_id,
                "commit_sha": sha,
                "commit_message": commit_msg,
                "workflow_name": workflow_name,
                "status": status,
                "workflow_duration": w_duration,
                "job_name": job_name,
                "job_duration": j_duration,
                **test_info,
                "timestamp": timestamp,
            })

            for step in job.get("steps", []):
                s_duration = _duration_seconds(
                    step.get("started_at", ""), step.get("completed_at", "")
                )
                steps_rows.append({
                    "run_id": run_id,
                    "job_name": job_name,
                    "step_name": step.get("name", ""),
                    "step_duration": s_duration,
                    "timestamp": timestamp,
                })

    # Save metrics.csv
    metrics_path = os.path.join(DATA_DIR, "metrics.csv")
    metrics_cols = [
        "run_id", "commit_sha", "commit_message", "workflow_name", "status",
        "workflow_duration", "job_name", "job_duration",
        "test_count", "test_failures", "test_errors", "test_duration_total",
        "timestamp",
    ]
    with open(metrics_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metrics_cols)
        writer.writeheader()
        writer.writerows(metrics_rows)
    print(f"\nSaved {len(metrics_rows)} rows → {metrics_path}")

    # Save metrics.json
    json_path = os.path.join(DATA_DIR, "metrics.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_rows, f, indent=2, ensure_ascii=False)
    print(f"Saved JSON → {json_path}")

    # Save steps_detail.csv
    steps_path = os.path.join(DATA_DIR, "steps_detail.csv")
    steps_cols = ["run_id", "job_name", "step_name", "step_duration", "timestamp"]
    with open(steps_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=steps_cols)
        writer.writeheader()
        writer.writerows(steps_rows)
    print(f"Saved {len(steps_rows)} step rows → {steps_path}")

    # Summary
    total_runs = len({r["run_id"] for r in metrics_rows})
    success_runs = len({
        r["run_id"] for r in metrics_rows if r["status"] == "success"
    })
    success_rate = (success_runs / total_runs * 100) if total_runs else 0.0

    unique_runs = {}
    for r in metrics_rows:
        rid = r["run_id"]
        if rid not in unique_runs:
            unique_runs[rid] = r["workflow_duration"]
    avg_duration = (
        sum(unique_runs.values()) / len(unique_runs) if unique_runs else 0.0
    )

    job_durations: dict[str, list] = {}
    for r in metrics_rows:
        if r["job_name"]:
            job_durations.setdefault(r["job_name"], []).append(r["job_duration"])
    slowest_job = (
        max(job_durations, key=lambda j: sum(job_durations[j]) / len(job_durations[j]))
        if job_durations else "N/A"
    )

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"  Total runs collected : {total_runs}")
    print(f"  Success rate         : {success_rate:.1f}%")
    print(f"  Avg workflow duration: {avg_duration:.1f}s")
    print(f"  Slowest job (avg)    : {slowest_job}")


if __name__ == "__main__":
    collect()
