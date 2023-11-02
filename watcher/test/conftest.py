import contextlib
from unittest import mock

import pytest


@pytest.fixture(autouse=True)
def prohibit_network():
    with contextlib.ExitStack() as stack:
        for import_path in (
            'socket.socket',
            'socket.create_connection',
        ):
            stack.enter_context(
                mock.patch(
                    import_path,
                    side_effect=RuntimeError('Networking usage is prohibited')
                )
            )
        yield
