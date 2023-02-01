import argparse

from dronenet import db
from dronenet.models import Remote


#--------------------------------------------------------------------#
def _main() -> None:
  # parse command-line arguments
  parser = argparse.ArgumentParser(description='add_key.py', allow_abbrev=False, add_help=False)
  parser.add_argument('-h', '--help', action='help', help=argparse.SUPPRESS)
  parser.add_argument('--commit', action='store_true')
  parser.add_argument('--create', action='store_true', help='Creates a new database - this is needed if no database exists yet')
  parser.add_argument('--ip', type=str, default='')
  parser.add_argument('--name', type=str, default='')
  args = parser.parse_args()

  if args.create:
    db.create_all()

  if args.ip and args.name:
    # find unused id - this must be a very bad way of doing it
    _id = 0
    remote = None
    while True:
      _id += 1
      if not Remote.query.filter_by(id=_id).first():
        break

    # create a new remote
    remote = Remote(id=_id, ip=args.ip, name=args.name)
    print(f'New remote:           {remote}')

    if Remote.query.filter_by(ip=args.ip).first():
      print(f'Conflict in database: {Remote.query.filter_by(ip=args.ip).first()}')
      args.commit = False

    if remote and args.commit:
      # add new remote to database
      db.session.add(remote)
      db.session.commit()

  # print list of all remotes
  print("\nList of all remotes:")
  for remote in Remote.query.all():
    print(remote)


#--------------------------------------------------------------------#
if __name__ == '__main__':
  _main()
