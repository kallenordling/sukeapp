import sys
import logging

logging.basicConfig(filename='/var/www/html/suke/suke.log')
sys.path.insert(0, '/var/www/html/suke')

from run import app as application
