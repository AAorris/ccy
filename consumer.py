"""Retrieve data from the server."""

import argparse
import requests


def main():
    """Run the program."""
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('token')
    args = parser.parse_args()
    with open(args.token, 'a') as output:
        response = requests.get(args.url)
        response.raise_for_status()
        output.write(response.text)


if __name__ == '__main__':
    main()
