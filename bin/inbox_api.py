#!/usr/bin/env python
import os
import sys
import signal
import click

# Check that the inbox package is installed. It seems Vagrant may sometimes
# fail to provision the box appropriately; this check is a reasonable
# approximation of "Did the setup script run?"
try:
    from inbox.config import config
except ImportError:
    sys.exit("Could not find Inbox installation. "
             "Maybe the Vagrant box provisioning didn't succeed?\n"
             "Try running sudo ./setup.sh")

from setproctitle import setproctitle; setproctitle('inbox-api')
from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer

from inbox.api.wsgi import InboxWSGIHandler
from inbox.log import get_logger, configure_logging
from inbox.util.startup import preflight, load_overrides


#super hack!
pynacl_path = filter(lambda path: "PyNaCl" in path, sys.path)
if len(pynacl_path):
    pynacl_path = pynacl_path[0]
    sys.path.append(os.path.join(pynacl_path, "PyNaCl-0.3.0_inbox.data",
                                 "purelib"))

syncback = None
http_server = None
def signal_handler(signum, frame):
    print 'Signal handler called with signal', signum
    try:
        syncback.stop()
    except:
        # Ignore errors while stopping, there's not much we can do at this
        # point.
        pass
    http_server.stop()
    sys.stdout.flush()


@click.command()
@click.option('--prod/--no-prod', default=False,
              help='Disables the autoreloader and potentially other '
                   'non-production features.')
@click.option('-c', '--config', default=None,
              help='Path to JSON configuration file.')
@click.option('-p', '--port', default=5555, help='Port to run flask app on.')
def main(prod, config, port):
    """ Launch the Inbox API service. """
    configure_logging(prod)

    if config is not None:
        config_path = os.path.abspath(config)
        load_overrides(config_path)

    if prod:
        start(port)
    else:
        from werkzeug.serving import run_with_reloader
        run_with_reloader(lambda: start(port))


def start(port):
    global syncback
    global http_server

    # We need to import this down here, because this in turn imports
    # ignition.engine, which has to happen *after* we read any config overrides
    # for the database parameters. Boo for imports with side-effects.
    from inbox.api.srv import app

    # Catch SIGTERM so that we can gracefully exit
    signal.signal(signal.SIGTERM, signal_handler)

    # start actions service
    from inbox.transactions.actions import SyncbackService
    syncback = SyncbackService()
    syncback.start()

    inbox_logger = get_logger()

    http_server = WSGIServer(('', int(port)), app, log=inbox_logger,
                             handler_class=InboxWSGIHandler)
    inbox_logger.info('Starting API server', port=port)
    try:
        http_server.serve_forever()
    except:
        # Shouldn't ever return, however when we kill due to signal handler,
        # sometimes an error is output that we simply want to ignore as there
        # isn't anything special we can do to handle it.
        pass

    syncback.join()
    print "exiting normally."


main()
