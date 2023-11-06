from __future__ import annotations

import contextlib
import email.message
import os
import re
import smtplib
from typing import Iterable


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


def make_email_message(
    sender: str, recievers: Iterable[str]
) -> email.message.EmailMessage:
    message = email.message.EmailMessage()
    message['From'] = sender
    message['To'] = ', '.join(recievers)
    return message
