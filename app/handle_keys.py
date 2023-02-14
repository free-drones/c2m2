import argparse
import json
import time

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
  parser.add_argument('--backup_create', action='store_true')
  parser.add_argument('--backup_load', type=str, default='')
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

  if args.backup_create:
    # print list of all remotes
    remotes={}
    for remote in Remote.query.all():
      remotes[remote.id] = {"ip": remote.ip, "name": remote.name}
    # Create a backup file and write to it
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = 'backup/'+ timestamp + '_remote_backup.json'
    with open(filename, 'w', encoding="utf-8") as outfile:
      # Write json struct
      outfile.write(json.dumps(remotes))
    print(f'Wrote backup to: {filename}')
    return

  if args.backup_load != '':
    with open(args.backup_load, 'r', encoding='utf-8') as infile:
            backup = json.load(infile)
            for id in backup:
              _add_remote(backup[id]['ip'], backup[id]['name'], args.commit)
    return

  if args.add and args.delete:
    print('ERROR: Both add and delete set to true')
    return

  if args.add:
    if args.ip and args.name:
      _add_remote(args.ip,args.name, args.commit)
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

# Add remote method
def _add_remote(_ip, _name, _commit):
  # find unused id - this must be a very bad way of doing it
  _id = 0
  remote = None
  while True:
    _id += 1
    if not Remote.query.filter_by(id=_id).first():
      break

  # create a new remote
  remote = Remote(id=_id, ip=_ip, name=_name)
  print(f'New remote:           {remote}')
  if Remote.query.filter_by(ip=_ip).first():
    print(f'Conflict in database: {Remote.query.filter_by(ip=_ip).first()}')
    print('Not adding remote due to conflict, ip already allocated')
    return

  if remote and _commit:
    # add new remote to database
    db.session.add(remote)
    db.session.commit()
  else:
    print('Not adding the new remote. Make sure that the commit argument is set to true')

#--------------------------------------------------------------------#
if __name__ == '__main__':
  _main()
