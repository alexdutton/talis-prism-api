import sys
from datetime import datetime, timedelta

from config import INSTANCES
from access import TalisPrism

def autorenew(base_url, username, password, buffer=timedelta(2)):
    tp = TalisPrism(base_url, username, password)
    items, to_renew = tp.loans, []
    for item in items:
        if item['due'] - datetime.now() < buffer:
            to_renew.append(item['lcn'])
    if to_renew:
        tp.renew(to_renew)
    print "Attempted to renew %d of %d items" % (len(to_renew), len(items))


if __name__ == '__main__':
    autorenew(getattr(INSTANCES, sys.argv[1]), *sys.argv[2:4])
