#!/usr/bin/env python

import argparse
import asyncio
from pathlib import Path
import os
import sys

from context import Context, RemoteContext, LocalContext
from log import error, info

import experiments


async def run(
    ctx: Context,
    local_result_path: Path,
    experiment_base: Path,
    experiment: experiments.Experiments,
) -> None:
    info(str(ctx))
    async with ctx as client:
        info(f"Open new context ({client.context()})")

        info("Copy data to context")
        await client.sync_to(experiment_root=experiment_base)

        info("Build and run benchmarks on remote machine")
        await client.run([f"cd experiments/{experiment}", "make"])

        info("Copy results back to local machine")
        await client.sync_back(
            remote_path=Path(f"experiments/{experiment}/results/"),
            local_path=local_result_path,
        )

    info("Done running experiments")

    info("Start plotting measurements")
    experiments.plot(local_result_path, experiment, format="pdf")

    info("--------- Done ---------")


def run_local(args):
    experiment = args.experiment
    experiment_root = args.base
    result_root = args.result
    cleanup = args.cleanup

    ctx = LocalContext(
        delete=cleanup,
    )
    asyncio.run(
        run(
            ctx=ctx,
            local_result_path=result_root,
            experiment_base=experiment_root,
            experiment=experiment,
        )
    )
    pass


def run_remote(args):
    remote_user = args.remote_user or os.getenv("MTE_REMOTE_USER")
    if not remote_user:
        error(f"--remote-user not provided and MTE_REMOTE_USER not set.")
        sys.exit(1)

    remote_host = args.remote_user or os.getenv("MTE_REMOTE_HOST")
    if not remote_host:
        error(f"--remote-host not provided and MTE_REMOTE_HOST not set.")
        sys.exit(1)

    remote_jump_user = args.remote_jump_user or os.getenv("MTE_REMOTE_JUMP_USER")
    remote_jump_host = args.remote_jump_host or os.getenv("MTE_REMOTE_JUMP_HOST")
    remote_jump_port = args.remote_jump_port or os.getenv("MTE_REMOTE_JUMP_PORT")
    if (
        any([remote_jump_user, remote_jump_host, remote_jump_port])
        and all([remote_jump_user, remote_jump_host]) == False
    ):
        error(
            (
                "must provide both "
                "--remote-jump-user (or set MTE_REMOTE_JUMP_USER) and "
                "--remote-jump-host (or set MTE_REMOTE_JUMP_HOST) "
                "or set neither"
            )
        )
        sys.exit(1)

    experiment = args.experiment
    experiment_root = args.base
    result_root = args.result
    cleanup = args.cleanup

    ctx = RemoteContext(
        remote_user=remote_user,
        remote_host=remote_host,
        jump_user=remote_jump_user,
        jump_host=remote_jump_host,
        jump_port=remote_jump_port,
        delete=cleanup,
    )
    asyncio.run(
        run(
            ctx=ctx,
            local_result_path=result_root,
            experiment_base=experiment_root,
            experiment=experiment,
        )
    )


def run_create(args):
    experiment = args.name
    experiment_base = Path(args.base)
    experiment_root = experiment_base / Path(experiment)
    if experiment_root.exists():
        error(f"Experiment with name '{experiment}' already exists")
        sys.exit(1)

    evaluation_script = Path(__file__).parent / Path("plot") / Path(f"{experiment}.py")
    if evaluation_script.exists():
        error(f"Experiment with name '{experiment}' already exists")
        sys.exit(1)

    experiment_root.mkdir(parents=True, exist_ok=True)
    makefile = experiment_root / Path("Makefile")
    makefile.write_text(("default:\n" "\techo Hello World\n"))

    evaluation_script = Path(__file__).parent / Path("plot") / Path(f"{experiment}.py")
    evaluation_script.write_text(
        (
            "from pathlib import Path\n\n"
            "def plot(output_root: Path, format):\n"
            "\tpass\n"
        )
    )

    experiments.verify_experiment(experiment_base, experiment)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="benchmark-tool",
        description="A tool for performing benchmarks on remote machines.",
    )

    experiment_root = Path(__file__).parent.parent / Path("experiments/")
    _ = parser.add_argument(
        "--base",
        default=str(experiment_root),
        type=str,
        help="The base directory in which the experiments are implemented.",
    )

    args, _ = parser.parse_known_args()
    discovered_experiments = experiments.discover_experiments(Path(args.base))
    choices = list(discovered_experiments.keys())
    experiments.set_experiments(discovered_experiments)

    def add_argument(p):
        result_root = Path(__file__).parent.parent / Path("results/")
        _ = p.add_argument(
            "--result",
            default=str(result_root),
            type=str,
            help="The base directory in which all the results are placed.",
        )

        _ = p.add_argument(
            "--cleanup",
            action="store_true",
            help="Cleanup all the resources of the context",
        )
        _ = p.add_argument(
            "--experiment",
            type=str,
            choices=choices,
            required=True,
            help="The experiment to run",
        )

    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create", help="Run the experiment locally.")
    create.add_argument(
        "--name",
        type=str,
        required=True,
        help="The name of the new experiment",
    )
    create.set_defaults(func=run_create)

    local = subparsers.add_parser("local", help="Run the experiment locally.")
    local.set_defaults(func=run_local)
    add_argument(local)

    remote = subparsers.add_parser("remote", help="Run the experiment remotely")
    remote.set_defaults(func=run_remote)
    add_argument(remote)

    remote.add_argument(
        "--remote-user", help="Remote username (or set MTE_REMOTE_USER)"
    )
    remote.add_argument("--remote-host", help="Remote host (or set MTE_REMOTE_HOST)")

    remote.add_argument(
        "--remote-jump-user", help="Remote jump user (or set MTE_REMOTE_JUMP_USER)"
    )
    remote.add_argument(
        "--remote-jump-host", help="Remote jump host (or set MTE_REMOTE_JUMP_HOST)"
    )
    remote.add_argument(
        "--remote-jump-port", help="Remote jump port (or set MTE_REMOTE_JUMP_PORT)"
    )

    args = parser.parse_args()
    args.func(args)
