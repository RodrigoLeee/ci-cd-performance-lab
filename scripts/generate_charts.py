"""Generate 4 analysis charts from data/metrics.csv."""
import os
import sys

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
except ImportError as exc:
    print(f"ERROR: Missing dependency — {exc}")
    print("Run: pip install pandas matplotlib numpy")
    sys.exit(1)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
CSV_PATH = os.path.join(DATA_DIR, "metrics.csv")

COLORS = {"success": "#2ecc71", "failure": "#e74c3c", "cancelled": "#f39c12"}
JOB_PALETTE = ["#3498db", "#e67e22", "#9b59b6", "#1abc9c", "#e74c3c"]


def _load_data() -> tuple:
    """Load and prepare the metrics CSV."""
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: {CSV_PATH} not found. Run collect_metrics.py first.")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)
    df["workflow_duration"] = pd.to_numeric(df["workflow_duration"], errors="coerce")
    df["job_duration"] = pd.to_numeric(df["job_duration"], errors="coerce")
    df["test_count"] = pd.to_numeric(df["test_count"], errors="coerce")
    df["test_failures"] = pd.to_numeric(df["test_failures"], errors="coerce").fillna(0)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    return df


def chart_01_pipeline_duration(df: pd.DataFrame) -> None:
    """Line + scatter: pipeline duration per execution."""
    runs = (
        df.drop_duplicates(subset="run_id")
        .sort_values("timestamp")
        .reset_index(drop=True)
    )
    runs["exec_num"] = range(1, len(runs) + 1)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        runs["exec_num"], runs["workflow_duration"],
        color="#2980b9", linewidth=1.5, zorder=1,
    )
    for _, row in runs.iterrows():
        color = COLORS.get(row["status"], "#95a5a6")
        ax.scatter(row["exec_num"], row["workflow_duration"], color=color, s=80, zorder=2)

    mean_dur = runs["workflow_duration"].mean()
    ax.axhline(mean_dur, color="#7f8c8d", linestyle="--", linewidth=1.2,
               label=f"Média: {mean_dur:.1f}s")

    xtick_labels = [f"{r['exec_num']}\n{r['commit_sha']}" for _, r in runs.iterrows()]
    ax.set_xticks(runs["exec_num"])
    ax.set_xticklabels(xtick_labels, fontsize=7)

    ax.set_xlabel("Número da Execução (commit SHA)", fontsize=11)
    ax.set_ylabel("Duração (s)", fontsize=11)
    ax.set_title("Duração Total do Pipeline por Execução", fontsize=13, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.6)

    legend_patches = [
        mpatches.Patch(color=COLORS["success"], label="Sucesso"),
        mpatches.Patch(color=COLORS["failure"], label="Falha"),
        mpatches.Patch(color="#7f8c8d", label=f"Média ({mean_dur:.1f}s)"),
    ]
    ax.legend(handles=legend_patches, fontsize=9)

    out = os.path.join(REPORTS_DIR, "chart_01_pipeline_duration.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


def chart_02_job_duration(df: pd.DataFrame) -> None:
    """Grouped bar chart: duration per job per execution."""
    job_df = df[df["job_name"].notna() & (df["job_name"] != "")].copy()
    if job_df.empty:
        print("Warning: no job data for chart 02.")
        return

    pivot = (
        job_df.groupby(["run_id", "job_name"])["job_duration"]
        .mean()
        .unstack(fill_value=0)
        .reset_index()
    )
    # Add short commit sha label
    sha_map = df.drop_duplicates("run_id").set_index("run_id")["commit_sha"].to_dict()
    pivot["label"] = pivot["run_id"].map(lambda r: sha_map.get(r, str(r))[:8])

    job_names = [c for c in pivot.columns if c not in ("run_id", "label")]
    n_runs = len(pivot)
    n_jobs = len(job_names)
    x = np.arange(n_runs)
    width = 0.8 / n_jobs

    fig, ax = plt.subplots(figsize=(max(10, n_runs * 1.5), 5))
    for i, job in enumerate(job_names):
        offset = (i - n_jobs / 2 + 0.5) * width
        color = JOB_PALETTE[i % len(JOB_PALETTE)]
        ax.bar(x + offset, pivot[job], width, label=job, color=color, alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(pivot["label"], rotation=45, ha="right", fontsize=8)
    ax.set_xlabel("Execução (commit SHA)", fontsize=11)
    ax.set_ylabel("Duração (s)", fontsize=11)
    ax.set_title("Duração por Job em Cada Execução", fontsize=13, fontweight="bold")
    ax.legend(title="Job", fontsize=9)
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)

    out = os.path.join(REPORTS_DIR, "chart_02_job_duration.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


def chart_03_success_rate(df: pd.DataFrame) -> None:
    """Pie + grouped bar: success/failure proportion and by workflow."""
    runs = df.drop_duplicates(subset="run_id").copy()
    status_counts = runs["status"].value_counts()

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Pie
    pie_labels = status_counts.index.tolist()
    pie_colors = [COLORS.get(s, "#95a5a6") for s in pie_labels]
    axes[0].pie(
        status_counts.values,
        labels=pie_labels,
        colors=pie_colors,
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"edgecolor": "white"},
    )
    axes[0].set_title("Proporção Sucesso / Falha", fontsize=12, fontweight="bold")

    # Bar by workflow
    wf_status = (
        runs.groupby(["workflow_name", "status"]).size().unstack(fill_value=0)
    )
    wf_names = wf_status.index.tolist()
    statuses = [s for s in ["success", "failure", "cancelled"] if s in wf_status.columns]
    x = np.arange(len(wf_names))
    width = 0.25

    for i, s in enumerate(statuses):
        offset = (i - len(statuses) / 2 + 0.5) * width
        axes[1].bar(
            x + offset, wf_status[s], width,
            label=s.capitalize(), color=COLORS.get(s, "#95a5a6"), alpha=0.85,
        )

    axes[1].set_xticks(x)
    axes[1].set_xticklabels(wf_names, fontsize=10)
    axes[1].set_ylabel("Contagem", fontsize=11)
    axes[1].set_title("Sucesso/Falha por Workflow", fontsize=12, fontweight="bold")
    axes[1].legend(fontsize=9)
    axes[1].grid(True, axis="y", linestyle=":", alpha=0.6)

    fig.suptitle(
        "Taxa de Sucesso e Falha por Workflow", fontsize=13, fontweight="bold", y=1.02
    )
    out = os.path.join(REPORTS_DIR, "chart_03_success_rate.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


def chart_04_tests_vs_duration(df: pd.DataFrame) -> None:
    """Scatter: test_count vs workflow_duration with trend line."""
    runs = df.drop_duplicates(subset="run_id").copy()
    scatter_df = runs[runs["test_count"].notna() & runs["workflow_duration"].notna()]

    if scatter_df.empty:
        print("Warning: no test_count data for chart 04.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    workflows = scatter_df["workflow_name"].unique()
    wf_colors = {wf: JOB_PALETTE[i % len(JOB_PALETTE)] for i, wf in enumerate(workflows)}

    for wf in workflows:
        sub = scatter_df[scatter_df["workflow_name"] == wf]
        sizes = (sub["test_failures"].fillna(0) + 1) * 50
        ax.scatter(
            sub["test_count"], sub["workflow_duration"],
            s=sizes, color=wf_colors[wf], alpha=0.75, label=wf, edgecolors="white",
        )

    # Trend line
    x_all = scatter_df["test_count"].values
    y_all = scatter_df["workflow_duration"].values
    if len(x_all) >= 2:
        coeffs = np.polyfit(x_all, y_all, 1)
        x_line = np.linspace(x_all.min(), x_all.max(), 100)
        y_line = np.polyval(coeffs, x_line)
        ax.plot(x_line, y_line, color="#2c3e50", linestyle="--", linewidth=1.5,
                label=f"Tendência (y={coeffs[0]:.2f}x+{coeffs[1]:.2f})")

    ax.set_xlabel("Quantidade de Testes", fontsize=11)
    ax.set_ylabel("Duração do Pipeline (s)", fontsize=11)
    ax.set_title(
        "Relação entre Quantidade de Testes e Duração do Pipeline",
        fontsize=13, fontweight="bold",
    )
    ax.legend(fontsize=9)
    ax.grid(True, linestyle=":", alpha=0.6)

    note = "Tamanho do ponto proporcional ao número de falhas (+1)"
    ax.annotate(note, xy=(0.01, 0.99), xycoords="axes fraction",
                va="top", fontsize=8, color="#7f8c8d")

    out = os.path.join(REPORTS_DIR, "chart_04_tests_vs_duration.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


def main() -> None:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    df = _load_data()
    print(f"Loaded {len(df)} rows from {CSV_PATH}")

    chart_01_pipeline_duration(df)
    chart_02_job_duration(df)
    chart_03_success_rate(df)
    chart_04_tests_vs_duration(df)

    print("\nAll 4 charts saved to reports/")


if __name__ == "__main__":
    main()
