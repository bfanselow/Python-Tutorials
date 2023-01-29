"""
 A simple python application daemon

 TODO: still need to write the server.Server() class

"""

import sys
import simplejson as json

# HACK: force all modules to use simplejson
sys.modules["json"] = json

import argparse
import logging
import logging.handlers
import signal


from app_daemon import server, configs, utils


LOG_FILE = '/var/log/app-daemon.log'


def _main():
    """
    Entry point of app daemon.
    """
    # Parse command line arguments.
    argp = argparse.ArgumentParser()
    argp.add_argument('-v', '--verbose', action='store_true')
    argp.add_argument('--profile', action='store_true')
    args = argp.parse_args()

    # Set up logging.
    log_level = logging.DEBUG if args.verbose else logging.INFO


    # Logrotate-friendly log file.
    handler = logging.handlers.WatchedFileHandler(LOG_FILE)
    handler.setLevel(log_level)
    logger.addHandler(handler)


    signal.signal(signal.SIGTERM, _on_sigterm)

    # Start serving.
    the_server = server.Server(listen_cfg['address'], listen_cfg['port'], cfg, profile=args.profile)
    the_server.run()


def _on_sigterm(signum, frame):
    """
    Handle SIGTERM signal, which is what ``kill`` sends.
    """
    # Server.run() will catch this.
    raise KeyboardInterrupt()


def main():
    """
    Entry point
    """
    try:
        _main()
    except Exception:
        utils.log_exception('Unhandled exception.')
        return 1
