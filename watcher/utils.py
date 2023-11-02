from __future__ import annotations

import contextlib
import os
import pathlib
import re
import smtplib


def get_smtp_auth():
    return (
        os.environ['WATCHER_SMTP_USER'],
        os.environ['WATCHER_SMTP_PASSWORD'],
    )


def get_smtp_endpoint():
    endpoint = os.environ['WATCHER_SMTP_ENDPOINT']
    if match := re.fullmatch(r'(?P<host>.+)\:(?P<port>\d+)', endpoint):
        return match.group('host'), int(match.group('port'))
    else:
        raise ValueError(f'Unsupported smtp endpoint format: {endpoint}')


@contextlib.contextmanager
def get_smtp_client():
    host, port = get_smtp_endpoint()
    user, password = get_smtp_auth()
    with smtplib.SMTP_SSL(host, port) as client:
        client.login(user, password)
        yield client


class SpecStateManager:

    def __init__(self, path: str | pathlib.Path):
        self._path = pathlib.Path(path)
        if not self._path.exists():
            self.mark_as_not_triggered()

    def is_triggered(self) -> str:
        with open(self._path) as f:
            return f.read() == '1'

    def mark_as_triggered(self):
        with open(self._path, 'w') as f:
            f.write('1')

    def mark_as_not_triggered(self):
        with open(self._path, 'w') as f:
            f.write('0')
