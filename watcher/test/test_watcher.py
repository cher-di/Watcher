import contextlib
import email.message
import os
import tempfile
from unittest import mock

import pytest

from watcher import __main__ as main
from watcher import specs
from watcher.specs import base


class FakeSpec(base.TwoStateSpec):

    @classmethod
    def name(cls) -> str:
        return 'fake_spec'

    def render_email_message(self, message: email.message.EmailMessage):
        message['Subject'] = 'Fake subject'
        message.set_content('Fake content')


class ActiveStateSpec(FakeSpec):

    def reached_active_state(self) -> bool:
        return True


class PassiveStateSpec(FakeSpec):

    def reached_active_state(self) -> bool:
        return False


@contextlib.contextmanager
def temporary_file(*args, **kwargs):
    fd, filepath = tempfile.mkstemp(*args, **kwargs)
    os.close(fd)
    try:
        yield filepath
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


@contextlib.contextmanager
def temporary_env_var(name, value):
    old_value = os.environ.get(name)
    os.environ[name] = value
    try:
        yield
    finally:
        if old_value is not None:
            os.environ[name] = old_value
        else:
            os.environ.pop(name)


@pytest.fixture
def spec_state_file():
    with temporary_file(prefix='state_', suffix='.txt') as spec_state_file_:
        os.remove(spec_state_file_)
        yield spec_state_file_


@pytest.fixture
def smtp():
    user, password = 'fake_smtp_user', 'fake_smtp_password'
    with contextlib.ExitStack() as stack:
        for name, value in (
            ('WATCHER_SMTP_USER', user),
            ('WATCHER_SMTP_PASSWORD', password),
            ('WATCHER_SMTP_ENDPOINT', 'smtp.fake_server.org:465')
        ):
            stack.enter_context(temporary_env_var(name, value))
        yield f'{user}@fake_server.org'


@contextlib.contextmanager
def mock_smtp():
    with mock.patch('smtplib.SMTP_SSL') as cls_mock:
        instance_mock = cls_mock.return_value
        instance_mock.__enter__.return_value = instance_mock
        yield instance_mock


def test_spec_not_reached_state(smtp, spec_state_file):
    with contextlib.ExitStack() as stack:
        stack.enter_context(
            mock.patch.object(
                specs,
                'AVAILABLE_SPECS',
                [PassiveStateSpec]
            )
        )

        with mock_smtp() as smtp_mock:
            exit_code = main.main(
                [
                    os.path.basename(main.__file__),
                    '--sender', smtp,
                    '--recievers', smtp,
                    'fake_spec',
                    '--state-file', spec_state_file,
                ]
            )
            assert exit_code == 0
            smtp_mock.send_message.assert_not_called()


def test_spec_reached_state(smtp, spec_state_file):
    with contextlib.ExitStack() as stack:
        stack.enter_context(
            mock.patch.object(
                specs,
                'AVAILABLE_SPECS',
                [ActiveStateSpec]
            )
        )

        with mock_smtp() as smtp_mock:
            exit_code = main.main(
                [
                    os.path.basename(main.__file__),
                    '--sender', smtp,
                    '--recievers', smtp,
                    'fake_spec',
                    '--state-file', spec_state_file,
                ]
            )
            assert exit_code == 0
            smtp_mock.send_message.assert_called_once()

        with mock_smtp() as smtp_mock:
            exit_code = main.main(
                [
                    os.path.basename(main.__file__),
                    '--sender', smtp,
                    '--recievers', smtp,
                    'fake_spec',
                    '--state-file', spec_state_file,
                ]
            )
            assert exit_code == 0
            smtp_mock.send_message.assert_not_called()
