import sys
import logging

logging.basicConfig(filename='suke.log')
sys.path.insert(0, './suke')

from run import app as application
