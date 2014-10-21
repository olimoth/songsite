import os
import sys

sys.path.insert(0, '/var/www/songservice')
sys.path.insert(0, '/var/www/songservice/dev/local/lib/python2.7/site-packages/')

import songservice
songservice.main()
from songservice import app as application
