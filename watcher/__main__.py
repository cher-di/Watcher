import argparse
import contextlib
import logging
import sys
from typing import Sequence, Type

from watcher import specs
from watcher import utils
from watcher.specs import base


logging.basicConfig(
    stream=sys.stderr,
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO
)


def parse_args(raw_args: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(raw_args[0])
    parser.add_argument(
        '--sender',
        help='Email address of sender',
        required=True
    )
    parser.add_argument(
        '--recievers',
        help='Email addresses of recievers, divided by comma',
        required=True,
        type=lambda value: value.split(',') if value is not None else []
    )

    subparsers = parser.add_subparsers(help='specs arguments')
    for spec in specs.AVAILABLE_SPECS:
        spec_parser = subparsers.add_parser(spec.name())
        spec.add_arguments(spec_parser)
        spec_parser.set_defaults(spec=spec)

    args = parser.parse_args(raw_args[1:])
    args.spec.validate_arguments(parser, args)

    return args


def main(raw_args: Sequence[str]) -> int:
    args = parse_args(raw_args)

    spec_cls: Type[base.Spec] = args.spec
    logging.info('Using spec %s', spec_cls.name())

    try:
        with contextlib.ExitStack() as stack:
            spec = stack.enter_context(spec_cls.from_args(args))
            if spec.need_to_notify():
                logging.info('Sending notification')
                message = utils.make_email_message(args.sender, args.recievers)
                spec.render_email_message(message)
                smtp_client = stack.enter_context(utils.get_smtp_client())
                smtp_client.send_message(message)
    except Exception:
        logging.exception('Exception occurred while processing spec:')
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[:]))
