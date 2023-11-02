from __future__ import annotations

import abc
import argparse
import email.message


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
    def from_args(cls, args: argparse.Namespace):
        return cls()

    @abc.abstractmethod
    def reached_state(self) -> bool:
        pass

    @abc.abstractmethod
    def render_email_message(self) -> email.message.EmailMessage:
        pass
