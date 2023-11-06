from __future__ import annotations

import abc
import argparse
import email.message
import enum
import pathlib
from typing import Optional


class Spec(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def name(cls) -> str:
        pass

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser):
        pass

    @classmethod
    def validate_arguments(
        cls, parser: argparse.ArgumentParser, args: argparse.Namespace
    ):
        pass

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> Spec:
        return cls()

    def __enter__(self) -> Spec:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abc.abstractmethod
    def need_to_notify(self) -> bool:
        pass

    @abc.abstractmethod
    def render_email_message(self, message: email.message.Message):
        pass


class SpecState(enum.Enum):
    PASSIVE = '0'
    ACTIVE = '1'


class TwoStateSpec(Spec):

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser):
        parser.add_argument(
            '--state-file',
            help='File with spec state',
            required=True,
            type=pathlib.Path
        )

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> TwoStateSpec:
        return cls(args.state_file)

    def __init__(self, state_file: pathlib.Path):
        self._state_file = state_file
        self._state: Optional[SpecState] = None

    def __enter__(self):
        self._state = SpecState.PASSIVE
        if self._state_file.exists():
            with open(self._state_file) as f:
                self._state = SpecState(f.read())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            with open(self._state_file, 'w') as f:
                return f.write(self._state.value)

    def need_to_notify(self) -> bool:
        assert self._state is not None, (
            'Spec with two states should be used only as contextmanager'
        )
        if (
            self._state == SpecState.PASSIVE
            and self.reached_active_state()
        ):
            self._state = SpecState.ACTIVE
            return True
        return False

    @abc.abstractmethod
    def reached_active_state(self) -> bool:
        pass
