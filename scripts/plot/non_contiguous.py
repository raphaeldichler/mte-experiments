from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def plot(output_root: Path, format):
    output_root = output_root / Path("non_contiguous")
    mte_enabled_csv = output_root / Path("load_mte.csv")
    mte_disabled_csv = output_root / Path("load.csv")

    enabled_df = pd.read_csv(mte_enabled_csv, sep=";")
    disabled_df = pd.read_csv(mte_disabled_csv, sep=";")

    for df in [enabled_df, disabled_df]:
        df["duration"] = df["duration"] / 1_000_000
        df["kb"] = df["len"] * 16 // 1024

    enabled_grouped = (
        enabled_df.groupby("kb")["duration"].agg(["mean", "std"]).reset_index()
    )
    disabled_grouped = (
        disabled_df.groupby("kb")["duration"].agg(["mean", "std"]).reset_index()
    )

    _, ax1 = plt.subplots(figsize=(10, 6))
    ax1.errorbar(
        enabled_grouped["kb"],
        enabled_grouped["mean"],
        yerr=enabled_grouped["std"],
        capsize=5,
        color="#a6bddb",
        linewidth=2.5,
        label="MTE enabled",
    )
    ax1.errorbar(
        disabled_grouped["kb"],
        disabled_grouped["mean"],
        yerr=disabled_grouped["std"],
        capsize=5,
        color="#fc9272",
        linewidth=2.5,
        label="MTE disabled",
    )

    ax1.set_xscale("log", base=2)
    ax1.set_yscale("log", base=2)

    tick_positions = enabled_grouped["kb"].iloc[::2]
    tick_labels = [
        f"{v} KiB" if v < 1024 else f"{v // 1024} MiB" for v in tick_positions
    ]
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels(tick_labels, rotation=45, ha="right")

    plt.xticks()
    plt.yticks()

    enabled_grouped["lower"] = enabled_grouped["mean"] - enabled_grouped["std"]
    disabled_grouped["lower"] = disabled_grouped["mean"] - disabled_grouped["std"]
    enabled_grouped["upper"] = enabled_grouped["mean"] + enabled_grouped["std"]
    disabled_grouped["upper"] = disabled_grouped["mean"] + disabled_grouped["std"]

    overlap = (disabled_grouped["lower"] <= enabled_grouped["upper"]) & (
        disabled_grouped["upper"] >= enabled_grouped["lower"]
    )

    enabled_grouped["percentage_diff"] = (
        (enabled_grouped["mean"] - disabled_grouped["mean"]) / enabled_grouped["mean"]
    ) * 100
    enabled_grouped.loc[overlap, "percentage_diff"] = 0

    ax2 = ax1.twinx()
    ax2.plot(
        enabled_grouped["kb"],
        enabled_grouped["percentage_diff"],
        "r--",
        label="% Difference",
    )
    ax2.set_ylabel("Difference (%)", fontsize=12)
    ax2.set_ylim(
        min(enabled_grouped["percentage_diff"]),
        max(enabled_grouped["percentage_diff"]) + 10,
    )

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()

    ax1.legend(loc="upper left", handles=h1 + h2, labels=l1 + l2)

    ax1.set_ylabel("Time (ns - logarithmic scale)")
    ax1.set_xlabel("Memory size (logarithmic scale)")

    plt.title("Lower is better ↓", color="navy")

    ax1.grid(True, which="both", linestyle=":", linewidth=0.5)
    plt.tight_layout()

    output = output_root / Path(f"result.{format}")
    plt.savefig(output, format=format)
