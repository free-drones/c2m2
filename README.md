# Deploying Flask app with uwsgi and nginx

## Step 1 — Installing nginx

Because Nginx is available in Ubuntu’s default repositories, it is possible to install it from these repositories using the `apt` packaging system.

Since this is our first interaction with the `apt` packaging system in this session, we will update our local package index so that we have access to the most recent package listings. Afterward, we can install `nginx`:

> sudo apt update

> sudo apt install nginx

## Step 2 — Checking the web server

At the end of the installation process, Ubuntu 18.04 starts Nginx. The web server should already be up and running.

We can check with the `systemd` init system to make sure the service is running by typing:

> sudo systemctl status nginx

As you can see below, the service appears to have started successfully.

    ● nginx.service - A high performance web server and a reverse proxy server
         Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
         Active: active (running) since Mon 2021-11-01 16:47:58 CET; 54min ago
           Docs: man:nginx(8)
        Process: 773234 ExecStartPre=/usr/sbin/nginx -t -q -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
        Process: 773245 ExecStart=/usr/sbin/nginx -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
       Main PID: 773246 (nginx)
          Tasks: 2 (limit: 1071)
         Memory: 3.0M
         CGroup: /system.slice/nginx.service
                 ├─773246 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
                 └─773250 nginx: worker process

    Nov 01 16:47:57 dronenet systemd[1]: Starting A high performance web server and a reverse proxy server...
    Nov 01 16:47:58 dronenet systemd[1]: Started A high performance web server and a reverse proxy server.


However, the best way to test this is to actually request a page from Nginx.

When you have your server’s IP address, enter it into your browser’s address bar: http://10.44.160.10/

You should see the default Nginx landing page.

## Step 3 — Managing the nginx process

Now that you have your web server up and running, let's review some basic management commands.

To stop the web server, type:
> sudo systemctl stop nginx

To start the web server, type:
> sudo systemctl start nginx

To stop and then start the service again, type:
> sudo systemctl restart nginx

If you are simply making configuration changes, nginx can often reload without dropping connections. To do this, type:
> sudo systemctl reload nginx

By default, nginx is configured to start automatically when the server boots. If this is not what you want, you can disable this behavior by typing:
> sudo systemctl disable nginx

To re-enable the service to start up at boot, you can type:
> sudo systemctl enable nginx

## Step 4 — Installing the Components from the Ubuntu Repositories

Our first step will be to install all of the pieces that we need from the Ubuntu repositories. We will install `pip3`, the Python package manager, to manage our Python components. We will also get the Python development files necessary to build uWSGI.

First, let's update the local package index and install the packages that will allow us to build our Python environment. These will include `python-pip3`, along with a few more packages and development tools necessary for a robust programming environment:

> sudo apt update

> sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools

With these packages in place, let's move on to creating a virtual environment for our project.

## Step 5 — Creating a Python Virtual Environment

Next, we'll set up a virtual environment in order to isolate our Flask application from the other Python files on the system.

Start by installing the `python3-venv` package, which will install the venv module:

> pip3 install virtualenv

Next, let's make a parent directory for our Flask project. Move into the directory after you create it:

> mkdir ~/c2m2

> cd ~/c2m2

Create a virtual environment to store your Flask project’s Python requirements by typing:

> python3 -m virtualenv .env

This will install a local copy of Python and pip into a directory called .env within your project directory.

Before installing applications within the virtual environment, you need to activate it. Do so by typing:

> source .env/bin/activate

Your prompt will change to indicate that you are now operating within the virtual environment. It will look something like this

    (.env)
    lennart@dronenet ~/c2m2

# Step 6 — Setting Up a Flask Application

Now that you are in your virtual environment, you can install Flask and uWSGI and get started on designing your application.

First, let's install wheel with the local instance of pip to ensure that our packages will install even if they are missing wheel archives:

> pip3 install wheel

Next, let's install Flask and uWSGI:

> pip3 install uwsgi flask

### Creating a Sample App

Now that you have Flask available, you can create a simple
application. Flask is a microframework. It does not include many of
the tools that more full-featured frameworks might, and exists mainly
as a module that you can import into your projects to assist you in
initializing a web application.

While your application might be more complex, we’ll create our Flask
app in a single file, called `c2m2.py`:

> nano ~/c2m2/c2m2.py

The application code will live in this file. It will import Flask and
instantiate a Flask object. You can use this to define the functions
that should be run when a specific route is requested:

    from flask import Flask

    app = Flask(__name__)

    @app.route("/")
    def hello():
        return "<h1 style='color:blue'>Hello There!</h1>"

    if __name__ == "__main__":
        app.run(host='10.44.160.10', port=6011)

This basically defines what content to present when the root domain is
accessed. Save and close the file when you're finished.

Now, you can test your Flask app by typing:

> python3 c2m2.py

You will see output like the following, including a helpful warning
reminding you not to use this server setup in production:

    Output
    * Serving Flask app c2m2 (lazy loading)
     * Environment: production
     WARNING: Do not use the development server in a production environment.
     Use a production WSGI server instead.
     * Debug mode: off
     * Running on http://10.44.160.10:6011/ (Press CTRL+C to quit)

When you are finished, hit CTRL-C in your terminal window to stop the
Flask development server.

### Creating the WSGI Entry Point

Next, let's create a file that will serve as the entry point for our
application. This will tell our uWSGI server how to interact with it.

Let’s call the file `wsgi.py`:

> nano ~/c2m2/wsgi.py

In this file, let's import the Flask instance from our application and
run it:

    from dronenet import app

    if __name__ == "__main__":
      app.run(host='10.44.160.10', port=5123)

Save and close the file when you are finished.

We’re now done with our virtual environment, so we can deactivate it:

> deactivate

Any Python commands will now use the system’s Python environment again.

### Creating a uWSGI Configuration File

You have tested that uWSGI is able to serve your application, but
ultimately you will want something more robust for long-term usage.
You can create a uWSGI configuration file with the relevant options
for this.

Let’s place that file in our project directory and call it `c2m2.ini`:

> nano ~/c2m2/c2m2.ini

Let’s put the content of our configuration file:

    [uwsgi]
    module = wsgi:app

    master = true
    processes = 5

    socket = c2m2.sock
    chmod-socket = 660
    vacuum = true

    die-on-term = true

    logto = /home/droneadmin/c2m2/c2m2.log

When you are finished, save and close the file.

## Step 7 — Creating a systemd Unit File

Next, let's create a systemd service unit file. Creating a systemd
unit file will allow Ubuntu’s init system to automatically start uWSGI
and serve the Flask application whenever the server boots.

Create a unit file ending in `.service` within the `/etc/systemd/`
system directory to begin:

> sudo nano /etc/systemd/system/c2m2.service

Let’s put the content of our server file:

    [Unit]
    Description=uWSGI instance to serve c2m2
    After=network.target

    [Service]
    User=droneadmin
    Group=www-data
    WorkingDirectory=/home/droneadmin/c2m2
    Environment="PATH=/home/droneadmin/c2m2/.env/bin"
    ExecStart=/home/droneadmin/c2m2/.env/bin/uwsgi --ini c2m2.ini

    [Install]
    WantedBy=multi-user.target

With that, our systemd service file is complete. Save and close it
now.

We can now start the uWSGI service we created and enable it so that it
starts at boot:

> sudo systemctl start c2m2
> sudo systemctl enable c2m2

Let’s check the status:

> sudo systemctl status c2m2

You should see output like this:

    ● c2m2.service - uWSGI instance to serve c2m2
         Loaded: loaded (/etc/systemd/system/c2m2.service; enabled; vendor preset: enabled)
         Active: active (running) since Mon 2021-11-01 16:48:05 CET; 44min ago
       Main PID: 773263 (uwsgi)
          Tasks: 6 (limit: 1071)
         Memory: 28.4M
         CGroup: /system.slice/c2m2.service
                 ├─773263 /home/lennart/c2m2/.env/bin/uwsgi --ini c2m2.ini
                 ├─773275 /home/lennart/c2m2/.env/bin/uwsgi --ini c2m2.ini
                 ├─773276 /home/lennart/c2m2/.env/bin/uwsgi --ini c2m2.ini
                 ├─773277 /home/lennart/c2m2/.env/bin/uwsgi --ini c2m2.ini
                 ├─773278 /home/lennart/c2m2/.env/bin/uwsgi --ini c2m2.ini
                 └─773279 /home/lennart/c2m2/.env/bin/uwsgi --ini c2m2.ini

    Nov 01 16:48:05 dronenet systemd[1]: Started uWSGI instance to serve c2m2.
    Nov 01 16:48:05 dronenet uwsgi[773263]: [uWSGI] getting INI configuration from c2m2.ini

If you see any errors, be sure to resolve them before continuing with the tutorial.

## Step 8 — Configuring Nginx to Proxy Requests

Our uWSGI application server should now be up and running, waiting for
requests on the socket file in the project directory. Let’s configure
Nginx to pass web requests to that socket using the `uwsgi` protocol.

Begin by creating a new server block configuration file in Nginx’s
`sites-available` directory. Let’s call this `c2m2` to keep in line
with the rest of the guide:

> sudo nano /etc/nginx/sites-available/c2m2

Open up a server block and tell Nginx to listen on the port `80`.
Let’s also tell it to use this block for requests for our server's
domain name:

    server {
        listen 80;
        listen 5123;
        server_name 10.44.160.10;

        location / {
            include uwsgi_params;
            uwsgi_pass unix:/home/lennart/c2m2/c2m2.sock;
        }
    }

socket.io variant:

    server {
        listen 5123;
        server_name 10.44.160.10;

        location / {
            include uwsgi_params;
            uwsgi_pass unix:/home/lennart/c2m2/c2m2.sock;
        }

        location /socket.io/ {
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            include uwsgi_params;
            uwsgi_pass unix:/home/lennart/c2m2/c2m2.sock;
        }
    }

Save and close the file when you're finished.

To enable the Nginx server block configuration you’ve just created,
link the file to the `sites-enabled` directory:

> sudo ln -s /etc/nginx/sites-available/c2m2 /etc/nginx/sites-enabled

With the file in that directory, we can test for syntax errors by typing:

> sudo nginx -t

If this returns without indicating any issues, restart the Nginx
process to read the new configuration:

> sudo systemctl restart nginx

You should now be able to navigate to your server’s domain name in
your web browser: http://10.44.160.10/

## Step 9 — Managing the application process

Now that you have your application up and running, let's review some
basic management commands.

To stop your application, type:
> sudo systemctl stop c2m2

To start the application when it is stopped, type:
> sudo systemctl start c2m2

To stop and then start the service again, type:
> sudo systemctl restart c2m2

To check the status of the application:
> sudo systemctl status c2m2

### Logs

#### Application Logs

`/home/lennart/c2m2/c2m2.log`: Every application request is recorded
is in this log file.

#### Server Logs

`/var/log/nginx/access.log`: Every request to your web server is
recorded in this log file unless Nginx is configured to do otherwise.

`/var/log/nginx/error.log`: Any Nginx errors will be recorded in this
log.

---

Credits: https://medium.com/swlh/deploy-flask-applications-with-uwsgi-and-nginx-on-ubuntu-18-04-2a47f378c3d2

---

# Installing dependencies

> source .env/bin/activate

> pip3 install -r requirements.txt

> deactivate
