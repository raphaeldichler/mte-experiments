from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot(output_root: Path, format):
    output_root = output_root / Path("cas")
    csv_file1 = output_root / Path("run.csv")
    csv_file2 = output_root / Path("run_mte.csv")

    df1 = pd.read_csv(csv_file1, sep=";")
    df2 = pd.read_csv(csv_file2, sep=";")

    df1["duration"] = df1["duration"] / 1_000_000_000
    df2["duration"] = df2["duration"] / 1_000_000_000

    grouped1 = df1.groupby("cores")["duration"].agg(["mean", "std"]).reset_index()
    grouped2 = df2.groupby("cores")["duration"].agg(["mean", "std"]).reset_index()

    merged = pd.merge(grouped1, grouped2, on="cores", suffixes=("_1", "_2"))

    _, ax1 = plt.subplots(figsize=(10, 6))

    library = ["1 Thread", "2 Threads", "3 Threads", "4 Threads"]
    x = np.arange(len(library))
    bar_width = 0.35

    ax1.bar(
        x - bar_width / 2,
        merged["mean_1"],
        yerr=merged["std_1"],
        width=bar_width,
        capsize=5,
        label="MTE disabled",
        color="#fc9272",
        edgecolor="black",
        linewidth=2,
    )
    ax1.bar(
        x + bar_width / 2,
        merged["mean_2"],
        yerr=merged["std_2"],
        width=bar_width,
        capsize=5,
        label="MTE enabled",
        color="#a6bddb",
        edgecolor="black",
        linewidth=2,
    )

    for i, row in merged.iterrows():
        x_start = i - 0.05

        y_start = row["mean_2"]
        y_end = row["mean_1"]

        if (y_start - row["std_2"]) <= (y_end + row["std_1"]):
            continue

        ax1.annotate(
            f"",
            xy=(x_start - 0.25 / 2, y_start),
            xytext=(x_start - 0.25 / 2, y_end + 0.05 * y_end),
            arrowprops=dict(arrowstyle="->", color="red", lw=2),
            color="red",
            ha="center",
        )

        percentage = y_start / y_end
        ax1.text(
            x_start - 0.25 / 2,
            y_start + ((y_end - y_start) / 2),
            f"{percentage:.2f}×",
            color="red",
            fontweight="bold",
            bbox=dict(facecolor="white", alpha=1.0, edgecolor="none"),
            ha="center",
        )

    plt.xticks(x, library)
    ax1.set_ylabel("Time (s)")
    ax1.set_xlabel(r"#Threads")

    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.set_title("Lower is better ↓", color="navy")
    ax1.legend(loc="upper left")
    ax1.set_ylim(ymin=0)

    output = output_root / Path(f"result.{format}")
    plt.savefig(output, format=format)
