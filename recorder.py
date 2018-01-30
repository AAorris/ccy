"""Collect live websocket data from binance into txt files.

Uses python's asyncio module and new syntax to collect
multiple streams at once.

Usage:
    python recorder.py ethbtc btcusdt

"""

import argparse
import asyncio
import json
import signal

import websockets

signal.signal(signal.SIGINT, signal.SIG_DFL)


async def track(token):
    """Connect to the web socket and append to the file.

    We check when the number of trades rolls back to zero to flush the file.
    Some events may be lost if the program closes in between flushes.

    We record every event, not just the final state of the bar.

    Args:
        token (str): to record

    """
    url = 'wss://stream.binance.com:9443/ws/{}@kline_1m'.format(token)
    print(f'[subscribing to {url}]')
    outputfile = open('{}.txt'.format(token), 'a')
    while True:
        try:
            async with websockets.connect(url) as websocket:
                last = None
                msg = None
                async for message in websocket:
                    payload = json.loads(message)
                    if last and payload['k']['n'] < last:
                        print(f'[bar complete for {token}]')
                        outputfile.flush()
                    last = payload['k']['n']
                    # t,E,T = start, current time, end time
                    # o,c = open, close price
                    # h,l = high, low price
                    # v,n = volume, num trades
                    msg = "{t},{E},{T},{o},{c},{h},{l},{v},{n}" \
                          .format(E=payload['E'], **payload['k'])
                    print(msg, file=outputfile)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed. Going to try reconnecting.")
        outputfile.flush()
    outputfile.close()


def main():
    """Run the main program."""
    parser = argparse.ArgumentParser()
    parser.add_argument('tokens', nargs='*', help='to track, like trxbtc')
    args = parser.parse_args()
    mainloop = asyncio.get_event_loop()
    try:
        group = asyncio.gather(*[track(token) for token in args.tokens])
        mainloop.run_until_complete(group)
    finally:
        mainloop.close()


if __name__ == '__main__':
    main()
