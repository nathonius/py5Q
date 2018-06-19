import argparse
from py5Q import py5Q

parser = argparse.ArgumentParser(description='Send signals to your 5Q.')
parser.add_argument('--no-cache', action='store_false', default=True, dest='cache')
subparsers = parser.add_subparsers()


def signalCommand(args):
    client = py5Q(cacheTokens=args.cache)
    if len(args.zones) > 1:
        client.batchSignal(args.zones, args.color, name=args.name, effect=args.effect, message=args.message,
                           shouldNotify=args.notify, isRead=args.read, isArchived=args.archived, isMuted=args.muted)
    else:
        client.signal(args.zones[0], args.color, name=args.name, effect=args.effect, message=args.message,
                      shouldNotify=args.notify, isRead=args.read, isArchived=args.archived, isMuted=args.muted)


def deleteCommand(args):
    client = py5Q(cacheTokens=args.cache)
    if args.all:
        client.deleteAll()
    else:
        for signal in args.signals:
            client.delete(signal)


parserSignal = subparsers.add_parser('signal')
parserSignal.add_argument('--zones', '-z', nargs='+', required=True)
parserSignal.add_argument('--color', '-c', required=True)
parserSignal.add_argument('--name', '-n', default='py5Q Signal')
parserSignal.add_argument('--effect', '-e', default='SET_COLOR')
parserSignal.add_argument('--message', '-m')
parserSignal.add_argument('--notify', action='store_true')
parserSignal.add_argument('--read', '-r', action='store_true')
parserSignal.add_argument('--archived', '-a', action='store_true')
parserSignal.add_argument('--muted', action='store_true')
parserSignal.set_defaults(func=signalCommand)

parserDelete = subparsers.add_parser('delete')
parserDelete.add_argument('--all', '-a', action='store_true')
parserDelete.add_argument('signals', nargs='*')
parserDelete.set_defaults(func=deleteCommand)

args = parser.parse_args()
args.func(args)
