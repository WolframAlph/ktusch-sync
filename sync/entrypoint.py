import logging.config
from os.path import join, abspath, normpath

import schedule

from sync.go import Sync

LOGGING_CONF_PATH = normpath(join(abspath(__file__), '../../config/logging.cfg'))

logging.config.fileConfig(LOGGING_CONF_PATH,
                          defaults={'logfilename': abspath(join(LOGGING_CONF_PATH, '../../logs/sync_logs.log'))})


def run():
    sync = Sync()
    schedule.every(10).seconds.do(sync.run)

    while True:
        schedule.run_pending()


if __name__ == '__main__':
    run()
