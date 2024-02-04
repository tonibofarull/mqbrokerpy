import argparse


def get_args():
    parser = argparse.ArgumentParser(description="MQTT broker.")
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=1234)
    parser.add_argument("--listen", type=int, default=5)
    parser.add_argument(
        "-l",
        "--log",
        dest="loglevel",
        choices=["DEBUG", "INFO"],
        help="Set the logging level",
        default="DEBUG",
    )
    return parser.parse_args()
