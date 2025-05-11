from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot(output_root: Path, format):
    output_root = output_root / Path("contiguous_tagging")
    labels = ["malloc", "stg", "st2g", "ldg", "ldr", "str"]
    csv_files = [
        output_root / Path("tag_malloc.csv"),
        output_root / Path("tag_stg.csv"),
        output_root / Path("tag_st2g.csv"),
        output_root / Path("ldg.csv"),
        output_root / Path("load.csv"),
        output_root / Path("store.csv"),
    ]

    dfs = []
    for file in csv_files:
        df = pd.read_csv(file, sep=";")
        df["duration"] = df["duration"]

        df["duration_per_op"] = df["duration"] / df["ops"]
        g = df.groupby("size")["duration_per_op"].agg(["mean", "std"]).reset_index()

        dfs.append(g)

    _, ax1 = plt.subplots(figsize=(10, 6))

    library = [""]
    colors = [
        "#a6bddb",
        "#fc9272",
        "#99d8c9",
        "#c994c7",
        "#fdbb84",
        "#efedf5",
        "skyblue",
    ]
    bar_width = 0.8 / len(csv_files)
    x = np.arange(len(library))

    group_mins = {}
    group_maxs = {}

    hatches = ["", "", "", "", "", "", ""]
    for i in range(len(csv_files)):
        df = dfs[i]
        mean_values = df["mean"].values

        for j, size in enumerate(df["size"].values):
            x_pos = x[j] + (i - (len(csv_files) - 1) / 2) * bar_width
            ax1.text(
                x_pos,
                mean_values[j],
                f"{mean_values[j]:.3f}",
                ha="center",
                va="bottom",
                color="black",
            )
            if size not in group_mins or mean_values[j] < group_mins[size][1]:
                group_mins[size] = (x_pos, mean_values[j])  # Store (x, min mean)
            if size not in group_maxs or mean_values[j] > group_maxs[size][1]:
                group_maxs[size] = (x_pos, mean_values[j])  # Store (x, max mean)

        _ = ax1.bar(
            x + (i - (len(csv_files) - 1) / 2) * bar_width,
            mean_values,
            yerr=df["std"],
            width=bar_width,
            capsize=5,
            label=labels[i],
            color=colors[i % len(colors)],
            edgecolor="black",
            hatch=hatches[i],
            linewidth=2,
        )

    ax1.set_ylabel("Time (ns)")
    ax1.set_xlabel("Single instruction")
    ax1.legend(labels=labels, loc="upper right")
    plt.title("Lower is better ↓", color="navy")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    plt.xticks(x, library, ha="right")
    ax1.set_ylim(ymin=0)
    plt.tight_layout()

    output = output_root / Path(f"result.{format}")
    plt.savefig(output, format=format)
