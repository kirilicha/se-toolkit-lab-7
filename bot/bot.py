import argparse

from handlers import handle_command


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, default=None)
    args = parser.parse_args()

    if args.test is not None:
        print(handle_command(args.test))
        return 0

    print("Telegram runtime is not implemented yet. Use --test mode.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
