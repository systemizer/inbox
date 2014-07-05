""" Code for propagating Inbox datastore changes to account backends.

Syncback actions don't update anything in the local datastore; the Inbox
datastore is updated asynchronously (see namespace.py) and bookkeeping about
the account backend state is updated when the changes show up in the mail sync
engine.

Dealing with write actions separately from read syncing allows us more
flexibility in responsiveness/latency on data propagation, and also makes us
unable to royally mess up a sync and e.g. accidentally delete a bunch of
messages on the account backend because our local datastore is messed up.

This read/write separation also allows us to easily disable syncback for
testing.

The main problem the separation presents is the fact that the read syncing
needs to deal with the fact that the local datastore may have new changes to
it that are not yet reflected in the account backend. In practice, this is
not really a problem because of the limited ways mail messages can change.
(For more details, see individual account backend submodules.)

ACTIONS MUST BE IDEMPOTENT! We are going to have task workers guarantee
at-least-once semantics.
"""
from inbox.actions.base import (archive, unarchive, star, unstar, mark_unread,
                                mark_read, mark_spam, unmark_spam, mark_trash,
                                unmark_trash, save_draft, delete_draft,
                                ActionError)

__all__ = ['archive', 'unarchive', 'star', 'unstar', 'mark_unread',
           'mark_read', 'mark_spam', 'unmark_spam', 'mark_trash',
           'unmark_trash', 'save_draft', 'delete_draft', 'ActionError']
