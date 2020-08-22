import logging.config
from os.path import join, abspath, normpath
from multiprocessing import Process
import time

import schedule

from business.sync.go import Sync

LOGGING_CONF_PATH = normpath(join(abspath(__file__), '../../config/logging.cfg'))

logging.config.fileConfig(LOGGING_CONF_PATH,
                          defaults={'logfilename': abspath(join(LOGGING_CONF_PATH, '../../logs/sync_logs.log'))})


def run():
    sync = Sync()
    schedule.every(10).seconds.do(sync.run)
    # TODO set cleanup of loggs
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            logging.exception(str(e))
            logging.info('Sync stopped')
            raise


class SyncProcess:

    def __init__(self):
        self.process = None
        self.started = None
        self.suspended = None

    @property
    def is_alive(self):
        return self.process.is_alive()

    @property
    def time_up(self):
        return time.time() - self.started if self.started else 0

    @property
    def time_suspended(self):
        return time.time() - self.suspended if self.suspended else 0

    def start(self):
        self.process = Process(name='sync-process', target=run)
        self.process.start()
        self.started = time.time()
        self.suspended = 0

    def stop(self):
        self.process.terminate()
        self.process.join()
        self.suspended = time.time()
        self.started = 0

