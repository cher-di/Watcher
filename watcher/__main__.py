import argparse
import logging
import pathlib
import sys
from typing import Sequence

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
        help='Email addresses of recievers',
        required=True,
        nargs='+'
    )
    parser.add_argument(
        '--spec-state-file',
        help='File with spec state',
        required=True,
        type=pathlib.Path
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

    spec: base.Spec = args.spec.from_args(args)
    logging.info('Using spec %s', spec.name())

    has_errors = False
    try:
        spec_state_manager = utils.SpecStateManager(args.spec_state_file)
        if spec_state_manager.is_triggered():
            logging.info('Spec was already triggered')
        elif spec.reached_state():
            logging.info('Spec reached state')
            message = spec.render_email_message()
            message['From'] = args.sender
            message['To'] = ', '.join(args.recievers)
            with utils.get_smtp_client() as smtp_client:
                smtp_client.send_message(message)
            spec_state_manager.mark_as_triggered()
        else:
            logging.info('Spec did not reach state')
    except Exception:
        logging.exception('Exception occurred while processing spec:')
        has_errors = True

    return 1 if has_errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[:]))
