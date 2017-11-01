#!/usr/bin/python
"""web-blocking

Usage:
  web-blocking.py scan reference 
  web-blocking.py scan isp
  web-blocking.py clean
  web-blocking.py

Options:
  -h --help     Show this screen.
  --version     Show version.
  --speed=<kn>  Speed in knots [default: 10].
  --moored      Moored (anchored) mine.
  --drifting    Drifting mine.

"""

__author__ = 'tofran'
__site__ = 'https://tofran.com/'

__license__ = "GPLv3"
__version__ = "2.0"
__maintainer__ = "tofran"
__email__ = "me@tofran.com"

##########


from docopt import docopt


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    print(arguments)
