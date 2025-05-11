from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def plot(output_root: Path, format):
    output_root = output_root / Path("contiguous")
    csv_file1 = output_root / Path("load16.csv")
    csv_file2 = output_root / Path("load16_mte.csv")

    df1 = pd.read_csv(csv_file1, sep=";")
    df2 = pd.read_csv(csv_file2, sep=";")

    df1["kb"] = df1["len"] * 64 // 1024
    df2["kb"] = df2["len"] * 64 // 1024

    grouped1 = df1.groupby("kb")["duration"].agg(["mean", "std"]).reset_index()
    grouped2 = df2.groupby("kb")["duration"].agg(["mean", "std"]).reset_index()

    merged = pd.merge(grouped1, grouped2, on="kb", suffixes=("_1", "_2"))

    _, ax1 = plt.subplots(figsize=(10, 6))

    ax1.errorbar(
        merged["kb"],
        merged["mean_1"],
        yerr=merged["std_1"],
        fmt="o-",
        color="#a6bddb",
        capsize=5,
        label="MTE disabled",
    )
    ax1.errorbar(
        merged["kb"],
        merged["mean_2"],
        yerr=merged["std_2"],
        fmt="s-",
        color="#fc9272",
        capsize=5,
        label="MTE enabled",
    )

    merged["lower_1"] = merged["mean_1"] - merged["std_1"]
    merged["lower_2"] = merged["mean_2"] - merged["std_2"]
    merged["upper_1"] = merged["mean_1"] + merged["std_1"]
    merged["upper_2"] = merged["mean_2"] + merged["std_2"]

    ax1.set_xscale("log", base=2)
    ax1.set_yscale("log", base=2)

    ax1.legend(loc="upper left")
    ax1.grid(True, which="both", linestyle="--", linewidth=0.5)

    xticks = grouped1["kb"].to_numpy()
    xticks_filtered = [x for i, x in enumerate(xticks) if i % 2 == 0]
    xtick_labels = [
        f"{int(x/1024)} MiB" if x >= 1024 else f"{int(x)} KiB" for x in xticks_filtered
    ]

    plt.xticks(xticks_filtered, xtick_labels, rotation=45, ha="right")

    plt.title("Lower is better ↓", color="navy")
    plt.ylabel("Time (ns - logarithmic scale)")
    plt.xlabel("Memory size (logarithmic scale)")

    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    plt.tight_layout()

    output = output_root / Path(f"result.{format}")
    plt.savefig(output, format=format)
