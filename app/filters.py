import logging

class IgnoreMigrationsFilter(logging.Filter):
    def filter(self, record):
        return 'migrations' not in record.pathname