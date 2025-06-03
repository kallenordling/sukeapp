import sys
import logging

logging.basicConfig(filename='suke.log')

sys.path.insert(0, '.')

from suke import app as application
