import sys
from typing import NoReturn

import md_kx._cli


def run() -> NoReturn:
    exit_code = md_kx._cli.run(sys.argv[1:])
    sys.exit(exit_code)


if __name__ == "__main__":
    run()
