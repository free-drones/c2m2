# c2m2 - web application for communication with CRM
This repository contains a web application for communicating with the Central Resource Manager in the RISE Drone System. It is a docker-based solution that launch a nginx web server and a Flask/uWSGI web application. Check the docker file and the docker compose file if you would like more information about what code that is running.

## Step 1 — Installing docker and docker compose

In order to run the application, you need to install docker and docker compose. For an installation guide, please go to https://docs.docker.com/engine/install/ and https://docs.docker.com/compose/install/ for details on how to install the docker engine and the docker compose plugin.

## Step 2 — Update the configuration file
The configuration file (.config in the config folder, not to confuse with the app/.config that is mirrored by docker-compose. It is a copy of the config/.config after each build) determines what projects that are used, the port to the associated CRM with the project and the IP address to the computer where the CRM is running. It could look something like this
```javascript
{
  "zeroMQ": {
    "subnets" : {
        "internal": {
            "ip": "127.0.0.",
            "crm_port": 12000
        },
        "local2": {
          "ip": "192.168.65.",
          "crm_port": 12000
          },
        "local": {
            "ip": "192.168.120.",
            "crm_port": 12000
        },
        "docker": {
          "ip": "172.17.0.",
          "crm_port": 12000
      }      
    }
  },
  "CRM" : {
    "comment": "Docker Host default ip is 172.17.0.1",
    "default_crm_ip": "172.20.10.6"
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
Install the requrements, preferably in a virtual env.
>python -m venv c2m2
>source c2m2/bin/activate
> pip install -r requirements.txt

The web application uses a database to handle the remote IPs that are allowed to connect to c2m2. To see what remote IPs that are added and accepted, use the following command
> python handle_keys.py --list

If it does not work, make sure that you have added the DSS to your python path (e.g. PYTHONPATH environment variable)! Another way is to run the python script within the docker container

> docker exec -it c2m2-c2m2-1 bash

> python handle_keys.py --list
libgl1 might be needed, install using apt if needed. 

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
