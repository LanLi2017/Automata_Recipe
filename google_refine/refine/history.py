"""
OpenRefine history: parsing responses.
"""


class HistoryEntry:
    # N.B. e.g. **response['historyEntry'] won't work as keys are unicode :-/
    def __init__(self, history_entry_id=None, time=None, description=None, **_):
        if history_entry_id is None:
            raise ValueError('History entry id must be set')
        self.id = history_entry_id
        self.description = description
        self.time = time
