import argparse
import asyncio

from handlers import handle_command


async def run_test_mode(text: str) -> None:
    result = await handle_command(text)
    print(result)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, default=None)
    args = parser.parse_args()

    if args.test is not None:
        asyncio.run(run_test_mode(args.test))
        return 0

    print("Telegram runtime is not implemented yet. Use --test mode.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
