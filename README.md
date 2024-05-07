# c2m2 - web application for communication with CRM
This repository contains a web application for communicating with the Central Resource Manager in the RISE Drone System. It is a docker-based solution that launch a nginx web server and a Flask/uWSGI web application. Check the docker file and the docker compose file if you would like more information about what code that is running.

## Step 1 — Installing docker and docker compose

In order to run the application, you need to install docker and docker compose. For an installation guide, please go to https://docs.docker.com/engine/install/ and https://docs.docker.com/compose/install/ for details on how to install the docker engine and the docker compose plugin.

## Step 2 — Update the configuration file
The configuration file (.config in the config folder) determines what projects that are used, the port to the associated CRM with the project and the IP address to the computer where the CRM is running. It could look something like this
```javascript
{
  "zeroMQ": {
    "subnets" : {
      "example1": {
        "ip": "10.44.161.",
        "crm_port": 16100
      },
      "example2": {
        "ip": "10.44.162.",
        "crm_port": 16200
      }
    }
  },
  "CRM" : {
    "default_crm_ip": "10.44.160.10"
  }
}
```
## Step 3 - Launch the web service
The web service can be launched by executing the command
> docker compose up --detach

Your user must belong to docker group, otherwise you will get permission denied errors. If so add your user to the docker 
group:
> sudo usermod -aG docker $USER

The command launches a container, and the detach flag makes sure that the service is running in the background. To check if the container is up and running, type:
> docker container list

and check if the container is active.

## Step 4 - Add the accepted remotes
The web application uses a database to handle the remote IPs that are allowed to connect to c2m2. To see what remote IPs that are added and accepted, use the following command
> python handle_keys.py --list

If it does not work, make sure that you have added the DSS to your python path (e.g. PYTHONPATH environment variable)! Another way is to run the python script within the docker container

> docker exec -it c2m2-c2m2-1 bash

> python handle_keys.py --list

If you would like to add remotes, type the following
> python handle_keys.py --add --ip 10.44.166.70 --name NAME_OF_REMOTE --commit

To remove remotes, you use the ID instead that is given to the remote once it has been added
> python handle_keys.py --delete --id 1 --commit

To create a backup of the remotes, use the the --backup_create flag
> python handle_keys.py --backup_create
It will create a time stamped backup file in json format in app/backup/

To load a backup of the remotes, use the --backup_load=[backup_file].
Duplicates will not be created.
> python handle_keys.py --backup_load='my_backup.json' --commit

## Step 5 - Maintenance
As of now, the app folder and the config file is mounted within the docker container, which means that you can modify the files "from the outside" without re-building the docker image. If you have done some modifications and would like to restart the service type:
> docker container kill c2m2-c2m2-1

> docker compose up

If you would like to re-build the docker image, use
> docker compose build --no-cache
