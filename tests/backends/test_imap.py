""" Tests IMAP backend functionality """

import pytest

from inbox.models.backends.imap import ImapAccount
from inbox.models.backends.yahoo import YahooAccount
from inbox.models.backends.gmail import GmailAccount

def test_backend_provider():
    """Tests whether the PROVIDER variable is set correctly for IMAP backends"""
    assert ImapAccount().provider == 'imap'
    assert GmailAccount().provider == 'gmail'
    assert YahooAccount().provider == 'yahoo'
