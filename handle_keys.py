import argparse

from dronenet import db
from dronenet.models import Remote


#--------------------------------------------------------------------#
def _main() -> None:
  # parse command-line arguments
  parser = argparse.ArgumentParser(description='handle_keys.py', allow_abbrev=False, add_help=False)
  parser.add_argument('-h', '--help', action='help', help=argparse.SUPPRESS)
  parser.add_argument('--commit', action='store_true')
  parser.add_argument('--add', action='store_true')
  parser.add_argument('--delete', action='store_true')
  parser.add_argument('--list', action='store_true')
  parser.add_argument('--id', type=int, default=-1)
  parser.add_argument('--ip', type=str, default='')
  parser.add_argument('--name', type=str, default='')
  args = parser.parse_args()

  #Check if database is initialized
  try:
    Remote.query.filter_by(id=1).first()
  except:
      print("Initializing database with table remote")
      db.session.execute("CREATE TABLE remote (id INT, ip VARCHAR(16), name VARCHAR(64))")

  if args.list:
    # print list of all remotes
      for remote in Remote.query.all():
        print(remote)

  if args.add and args.delete:
    print('ERROR: Both add and delete set to true')
    return

  if args.add:
    if args.ip and args.name:
      # find unused id - this must be a very bad way of doing it
      _id = 0
      remote = None
      first_entry = False
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
      else:
        print('Not adding the new remote. Make sure that the commit argument is set to true')
    else:
      print('IP and name required when adding a new entry')

  if args.delete:
    if args.id > -1:
      # Try to find the Remote in the database
      remote = Remote.query.filter_by(id=args.id).first()
      print(f'Remote to be removed: {remote}')
      if remote and args.commit:
        db.session.delete(remote)
        db.session.commit()
      else:
        print('Not deleting the remote. Make sure that the commit argument is set to true and/or that the ID is in the Remote list')
    else:
      print('ID required when deleting remote entries')



#--------------------------------------------------------------------#
if __name__ == '__main__':
  _main()
