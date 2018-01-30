"""Plot kline data from binance as an overlay.

Renders data from 0-100 (%) of measured min and max data.

Goal:
    identify low and high points relatively between currencies.

Usage:
    ls *.txt | xargs python viewer.py

"""

import argparse
from array import array
from matplotlib import pyplot as plotter


def percentile(data):
    """Convert an iterable to a percentile of min/max known from 0-1.

    Args:
        data (iterable[float]): like (1, 10, 100, 50, 100, 50)

    Returns:
        list[float]: like (0.01, 0.1, 1.0, 0.5, 1.0, 0.5)

    """
    vmax = max(data)
    vmin = min(data)
    return [((item - vmin) / (vmax - vmin)) for item in data]


def main():
    """Run the program."""
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*')
    filenames = parser.parse_args().filenames

    for filename in filenames:
        dates = array('f')
        numbers = array('f')
        for line in open(filename):
            dates.append(float(line.split(',')[1]))
            numbers.append(float(line.split(',')[3]))

        percentiles = percentile(numbers)
        del numbers
        plotter.figure(1)  # percentile
        plotter.plot(dates, percentiles, label=filename)
        plotter.figure(4)
        plotter.plot(dates[::800 * 4], percentiles[::800 * 4], label=filename)

    plotter.figure(1)
    plotter.legend()
    plotter.figure(4)
    plotter.legend()
    plotter.show()


if __name__ == '__main__':
    main()
