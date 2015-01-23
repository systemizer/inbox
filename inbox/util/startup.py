# XXX(dlitz): Most of this is deployment-related stuff that belongs outside the
# main Python invocation.
import gc
import os
import sys
import subprocess
import json
from pkg_resources import require, DistributionNotFound, VersionConflict

import sqlalchemy
from alembic.config import Config as alembic_config
from alembic.script import ScriptDirectory

from inbox.config import config

from inbox.log import get_logger
log = get_logger()


def _absolute_path(relative_path):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        relative_path)

def check_db():
    """ Checks the database revision against the known alembic migrations. """
    from inbox.ignition import main_engine
    inbox_db_engine = main_engine(pool_size=1, max_overflow=0)

    # top-level, with setup.sh
    alembic_ini_filename = os.environ.get("ALEMBIC_INI_PATH",
                                          _absolute_path('../../alembic.ini'))
    assert os.path.isfile(alembic_ini_filename), \
        'Must have alembic.ini file at {}'.format(alembic_ini_filename)
    alembic_cfg = alembic_config(alembic_ini_filename)

    try:
        inbox_db_engine.dialect.has_table(inbox_db_engine, 'alembic_version')
    except sqlalchemy.exc.OperationalError:
        sys.exit("Databases don't exist! Run bin/create-db")

    if inbox_db_engine.dialect.has_table(inbox_db_engine, 'alembic_version'):
        res = inbox_db_engine.execute('SELECT version_num from alembic_version')
        current_revision = [r for r in res][0][0]
        assert current_revision, \
            'Need current revision in alembic_version table...'

        script = ScriptDirectory.from_config(alembic_cfg)
        head_revision = script.get_current_head()
        log.info('Head database revision: {0}'.format(head_revision))
        log.info('Current database revision: {0}'.format(current_revision))
        # clean up a ton (8) of idle database connections
        del script
        gc.collect()

        if current_revision != head_revision:
            raise Exception(
                'Outdated database! Migrate using `alembic upgrade head`')
        else:
            log.info('[OK] Database scheme matches latest')
    else:
        raise Exception(
            'Un-stamped database! `bin/create-db` should have done this... bailing.')


def check_sudo():
    if os.getuid() == 0:
        raise Exception("Don't run Inbox as root!")


def load_overrides(file_path):
    """
    Convenience function for overriding default configuration.

    file_path : <string> the full path to a file containing valid
                JSON for configuration overrides
    """
    with open(file_path) as data_file:
        try:
            overrides = json.load(data_file)
        except ValueError:
            sys.exit('Failed parsing configuration file at {}'
                     .format(file_path))
        if not overrides:
            log.debug('No config overrides found.')
            return
        assert isinstance(overrides, dict), \
            'overrides must be dictionary'
        config.update(overrides)
        log.debug('Imported config overrides {}'.format(
            overrides.keys()))


def preflight():
    check_sudo()
    check_db()

    # Print a traceback when the process receives signal SIGSEGV, SIGFPE,
    # SIGABRT, SIGBUS or SIGILL
    import faulthandler
    faulthandler.enable()
