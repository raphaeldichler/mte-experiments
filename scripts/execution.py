import asyncio
from logging import info, error


async def run(command: str | list[str], cwd: str | None = None) -> str:
    if isinstance(command, list):
        command = " && ".join(command)

    command = command.strip()
    assert command.startswith("&&") == False, "already prefixed with '&&'"

    info(command)
    cp = await asyncio.create_subprocess_shell(
        cmd=command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
    )

    async def read_stream(stream, logger):
        lines = ""
        while True:
            line = await stream.readline()
            if not line:
                return lines
            line = line.decode().strip()
            lines += line
            logger(line)

    output: tuple[str, str] = await asyncio.gather(
        read_stream(cp.stdout, info),
        read_stream(cp.stderr, error),
    )

    _ = await cp.wait()
    if cp.returncode == 1:
        error("Failed.")
        exit(1)

    return output[0]
