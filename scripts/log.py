def log(prefix: str, msg: str, intend: int = 0):
    intend_offset = "\t" * intend
    for line in msg.split("\n"):
        if len(line) == 0:
            continue
        line = prefix + intend_offset + msg
        print(line, flush=True)


def info(msg: str, intend: int = 1):
    intend = intend + 1
    GREEN = "\033[32m"
    RESET = "\033[0m\033[39m"
    log(prefix=GREEN + "stdout>" + RESET, msg=msg, intend=intend)


def error(msg: str):
    RED = "\033[31m"
    RESET = "\033[0m\033[39m"
    log(prefix=RED + "stderr>" + RESET, msg=msg, intend=1)
