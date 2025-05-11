from typing import Callable, Literal
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

import importlib
import importlib.util

Experiments = Literal[
    "cas",
    "contiguous",
    "non_contiguous",
    "contiguous_tagging",
    "malloc",
    "parallel_non_contiguous",
]
PlottingFunction = Callable[[Path, str], None]
experiments: dict[str, PlottingFunction] | None = None


def set_experiments(discovered_experiments: dict[str, PlottingFunction]):
    global experiments
    experiments = discovered_experiments


def plot(output_root: Path, experiment: Experiments, format: Literal["pdf", "png"]):
    assert experiment, "invalid state, experiment discovery was not executed"
    rcParams = {
        "font.family": "serif",
        "font.size": 11,
        "pgf.rcfonts": False,
    }

    if format == "pdf":
        mpl.use("pdf")
        plt.rcParams["text.latex.preamble"] = r"\renewcommand{\mathdefault}[1][]{}"
        rcParams["pgf.texsystem"] = "pdflatex"

    mpl.rcParams.update(rcParams)
    experiments[experiment](output_root, format)


def verify_experiment(experiment_base: Path, experiment_name: str) -> None:
    experiment_directory = experiment_base / Path(experiment_name)
    if not experiment_directory.exists():
        raise Exception(f"Invalid state - cannot find experiment '{experiment_name}'.")

    makefile = experiment_directory / Path("Makefile")
    if not makefile.exists():
        raise Exception(
            f"Invalid state - cannot find Makefile for '{experiment_name}'."
        )

    evaluation_script = (
        Path(__file__).parent / Path("plot") / Path(f"{experiment_name}.py")
    )
    if not evaluation_script.exists():
        raise Exception(
            f"Invalid state - cannot find evaluation script for '{experiment_name}'."
        )


def discover_experiments(base: Path):
    experiments = {}

    evaluation_script = Path(__file__).parent / Path("plot")
    for file in evaluation_script.glob("*.py"):
        if file.name == "__init__.py":
            continue
        module_name = file.stem
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "plot"):
            experiments[module_name] = module.plot
        else:
            print("foo")

    experiment_source = set()
    for experiment in base.iterdir():
        if experiment.is_dir():
            experiment_source.add(experiment.name)

    return {k: v for k, v in experiments.items() if k in experiment_source}
