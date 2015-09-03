import logging
import logging.handlers

server_log = logging.getLogger("server")

fh = logging.FileHandler('test.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(levelname)s %(asctime)s %(module)s] %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# server_log.addHandler(fh)
# server_log.addHandler(ch)

# why print 2 log in console, and why this format has no effect on 'ch' ???
