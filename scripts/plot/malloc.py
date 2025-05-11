from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def run(csv_file1, csv_file2, duration_type, output, format):
    df1 = pd.read_csv(csv_file1, sep=";")
    df2 = pd.read_csv(csv_file2, sep=";")

    def norm(df):
        df["duration_allocation"] = df["duration_allocation"] / df["allocation"] / 1000
        df["duration_deallocation"] = (
            df["duration_deallocation"] / df["allocation"] / 1000
        )

    norm(df1)
    norm(df2)

    grouped1 = (
        df1.groupby("size")[["duration_allocation", "duration_deallocation"]]
        .agg(["mean", "std"])
        .reset_index()
    )
    grouped2 = (
        df2.groupby("size")[["duration_allocation", "duration_deallocation"]]
        .agg(["mean", "std"])
        .reset_index()
    )

    _, ax1 = plt.subplots(figsize=(12, 6))

    library = [
        "16 Bytes",
        "128 Bytes",
        "256 Bytes",
        "1024 Bytes",
        "2048 Bytes",
        "4096 Bytes",
        "8192 Bytes",
    ]
    x = np.arange(len(library))
    bar_width = 0.35

    bars1 = ax1.bar(
        x - bar_width / 2,
        grouped1[duration_type]["mean"],
        yerr=grouped1[duration_type]["std"],
        width=bar_width,
        capsize=5,
        label="MTE disabled",
        color="#a6bddb",
        edgecolor="black",
        linewidth=2,
    )
    bars2 = ax1.bar(
        x + bar_width / 2,
        grouped2[duration_type]["mean"],
        yerr=grouped2[duration_type]["std"],
        width=bar_width,
        capsize=5,
        label="MTE enabled",
        color="#fc9272",
        edgecolor="black",
        linewidth=2,
    )

    for i in range(len(bars1)):
        height2 = bars2[i].get_height()
        height1 = bars1[i].get_height()

        ax1.annotate(
            "",
            xy=(x[i] - bar_width / 2, height2),
            xytext=(x[i] - bar_width / 2, height1),
            arrowprops=dict(arrowstyle="->", color="red", lw=2),
            color="red",
            ha="center",
        )

        difference = height2 / height1
        ax1.text(
            i - bar_width / 2 - 0.04,
            height1 + ((height2 - height1) / 2) - 0.08,
            f"{difference:.2f}×",
            color="red",
            fontweight="bold",
            bbox=dict(facecolor="white", alpha=1.0, edgecolor="none"),
            ha="center",
        )

    plt.ylabel("Time (µs)")
    ax1.set_xlabel("Batch size")
    ax1.legend(loc="upper left")
    plt.title("Lower is better ↓", color="navy")

    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    plt.tight_layout()

    plt.xticks(x, library)
    plt.tight_layout()
    plt.savefig(output, format=format)


def plot(output_root: Path, format):
    output_root = output_root / Path("malloc")

    run(
        output_root / Path("malloc.csv"),
        output_root / Path("malloc_mte.csv"),
        "duration_allocation",
        output_root / Path(f"result-alloc.{format}"),
        format,
    )
    run(
        output_root / Path("malloc.csv"),
        output_root / Path("malloc_mte.csv"),
        "duration_deallocation",
        output_root / Path(f"result-dealloc.{format}"),
        format,
    )
