import logging

from core.orchestrator import collect_fares_once


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def main() -> None:
    collect_fares_once()


if __name__ == "__main__":
    main()