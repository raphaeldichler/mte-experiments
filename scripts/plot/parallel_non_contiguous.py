from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def run(csv_files: list[Path], output: Path, format):
    _, ax1 = plt.subplots(figsize=(10, 6))
    labels = ["MTE disabled", "MTE enabled"]

    data = []
    unique_threads = set()
    tick_positions = None
    for file in csv_files:
        df = pd.read_csv(file, sep=";")
        df["duration"] = df["duration"] // 1_000
        g = (
            df.groupby(["len", "threads"])["duration"]
            .agg(["mean", "std"])
            .reset_index()
        )
        g["kb"] = (g["len"] * 16) / 1024
        data.append(g)
        unique_threads.update(g["threads"].unique())
        tick_positions = g["kb"].unique()

    unique_threads = sorted(unique_threads)

    thread_colors = {1: "tomato", 2: "#56B4E9", 3: "#009E73", 4: "#E69F00"}

    line_styles = ["-", "--"]

    handles = []
    labels_legend = []

    for thread in unique_threads:
        for idx, g in enumerate(data):
            subset = g[g["threads"] == thread]
            if subset.empty:
                continue

            line = ax1.errorbar(
                subset["kb"],
                subset["mean"],
                yerr=subset["std"],
                fmt="o",
                linestyle=line_styles[idx],
                capsize=5,
                color=thread_colors.get(thread, "black"),
            )

            label = (
                f"1 Thread - {labels[idx]}"
                if thread == 1
                else f"{thread} Threads - {labels[idx]}"
            )
            handles.append(line[0])
            labels_legend.append(label)

    ax1.legend(
        handles=handles,
        labels=labels_legend,
        ncol=2,
        loc="upper left",
        fancybox=True,
        shadow=False,
    )

    ax1.set_xscale("log", base=2)
    ax1.set_yscale("log", base=2)

    ax1.grid(True, which="both", linestyle="--", linewidth=0.5)
    tick_labels = []
    xticks_filtered = [x for i, x in enumerate(tick_positions) if i % 2 == 0]
    for idx, v in enumerate(xticks_filtered):
        l = ""
        if v < 1024:
            if v < 1:
                l = "1 KiB"
            else:
                l = f"{v} KiB"
        else:
            l = f"{v // 1024} MiB"

        tick_labels.append(l)

    ax1.set_xticks(xticks_filtered)
    ax1.set_xticklabels(tick_labels, rotation=45, ha="right")
    ax1.set_ylabel("Time (ns - logarithmic scale)")
    ax1.set_xlabel("Memory size (logarithmic scale)")

    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    plt.title("Lower is better ↓", color="navy")
    plt.tight_layout()
    plt.savefig(output, format=format)


def plot(output_root: Path, format):
    output_root = output_root / Path("parallel_non_contiguous")

    run(
        [
            output_root / Path("write.csv"),
            output_root / Path("write_mte.csv"),
        ],
        output_root / Path(f"result-write.{format}"),
        format,
    )
    run(
        [
            output_root / Path("load.csv"),
            output_root / Path("load_mte.csv"),
        ],
        output_root / Path(f"result-read.{format}"),
        format,
    )
