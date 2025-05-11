from pathlib import Path
from typing import Protocol, Self
from execution import run
from log import info


class Context(Protocol):

    def context(self) -> str: ...

    async def sync_to(self, experiment_root: Path) -> None: ...

    async def run(self, cmd: str | list[str]) -> None: ...

    async def sync_back(self, remote_path: Path, local_path: Path) -> None: ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type, exc_value, exc_tb): ...


class RemoteContext:
    __remote_connection: str
    __jump_connection: str | None
    __cwd: str | None
    __delete: bool

    def __init__(
        self,
        remote_user: str,
        remote_host: str,
        jump_user: str | None = None,
        jump_host: str | None = None,
        jump_port: str | None = None,
        delete: bool = False,
    ) -> None:
        self.__cwd = None
        self.__delete = delete
        self.__remote_connection = f"{remote_user}@{remote_host}"
        self.__jump_connection = None

        if any([jump_host, jump_user, jump_port]):
            assert all([jump_host, jump_user]), "cannot define jump partially"
            self.__jump_connection = f"ssh -J {jump_user}@{jump_host}"
            if jump_port:
                self.__jump_connection += f" -p {jump_port}"

    def context(self) -> str:
        return f"Remote Context: {self.__cwd}"

    async def sync_to(self, experiment_root: Path) -> None:
        cmd = "rsync -avz"
        if self.__jump_connection:
            cmd += f" -e '{self.__jump_connection}'"

        cmd += f" {experiment_root} {self.__remote_connection}:{self.__cwd}"
        info(f"cmd: {cmd}")
        _ = await run(cmd)

    def __connection_cmd(self) -> str:
        connection_cmd = f"ssh {self.__remote_connection}"
        if self.__jump_connection:
            connection_cmd = f"{self.__jump_connection} {self.__remote_connection}"

        return connection_cmd

    async def run(self, cmd: str | list[str]) -> None:
        assert self.__cwd, "Cannot run command without setup"
        if isinstance(cmd, list):
            cmd = " && ".join(cmd)

        cmd = cmd.strip()
        assert cmd.startswith("&&") == False, "already prefixed with '&&'"

        _ = await run([f"{self.__connection_cmd()} 'cd {self.__cwd} && {cmd}'"])

    async def sync_back(self, remote_path: Path, local_path: Path) -> None:
        cmd = "rsync -avz"
        if self.__jump_connection:
            cmd += f" -e '{self.__jump_connection}'"

        cmd += f"{self.__remote_connection}:{self.__cwd}/{remote_path} {local_path}"
        _ = await run(cmd)

    async def __aenter__(self) -> Self:
        info("__aenter__")
        directory = await run(f"{self.__connection_cmd()} 'mktemp -d'")
        assert directory, "failed to create directory on remote system"
        self.__cwd = directory
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        assert self.__cwd, "incorrect state, cannot exit context which was not entered"
        if self.__delete:
            _ = await run(f"{self.__connection_cmd()} 'rm -rf {self.__cwd}'")


class LocalContext:
    __cwd: str | None
    __delete: bool

    def __init__(
        self,
        delete: bool = False,
    ) -> None:
        self.__cwd = None
        self.__delete = delete

    def context(self) -> str:
        return f"Local Context: {self.__cwd}"

    async def sync_to(self, experiment_root: Path) -> None:
        _ = await run(f"rsync -av {experiment_root} {self.cwd}")

    async def run(self, cmd: str | list[str]) -> None:
        assert self.cwd, "Cannot run command without setup"
        if isinstance(cmd, list):
            cmd = " && ".join(cmd)

        cmd = cmd.strip()
        assert cmd.startswith("&&") == False, "already prefixed with '&&'"

        _ = await run([f"cd {self.cwd} && {cmd}"])

    async def sync_back(self, remote_path: Path, local_path: Path) -> None:
        _ = await run(f"rsync -av {self.cwd}/{remote_path} {local_path}")

    async def __aenter__(self) -> Self:
        directory = await run("mktemp -d")
        assert directory, "failed to create directory on remote system"
        self.cwd = directory
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        assert self.cwd, "incorrect state, cannot exit context which was not entered"
        if self.__delete:
            _ = await run(f"rm -rf {self.__cwd}")
