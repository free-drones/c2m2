import datetime
import random
import time
from functools import wraps
import zmq
from flask import (Response, flash, redirect, render_template, request,
                   session, url_for)

from dronenet import app, db
from dronenet.camera import Camera
from dronenet.forms import SettingsForm
from dronenet.models import Remote

import dss.auxiliaries
from dss.auxiliaries.config import config

def get_project(ip):
  for project in config["zeroMQ"]["subnets"]:
    if config["zeroMQ"]["subnets"][project]["ip"] in ip:
      return project
  return None

class CRM_Monitor:
  def __init__(self, project):
    self.socket = None
    for config_project in config["zeroMQ"]["subnets"]:
      if config_project == project:
        self.socket = dss.auxiliaries.zmq.Req(zmq.Context(), config["CRM"]["default_crm_ip"], config["zeroMQ"]["subnets"][project]["subnet"]*100)
        break
    self.clients = list()

  def update_clients(self):
    answer = self.socket.send_and_receive({'id': 'root', 'fcn': 'clients', 'filter': ''})
    if dss.auxiliaries.zmq.is_ack(answer, 'clients'):
      clients = answer['clients']
      temp_clients = []
      for client_id, client in clients.items():
        client['id'] = client_id
        client['timestamp'] = datetime.datetime.utcfromtimestamp(client['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        temp_clients.append(client)
      self.clients = temp_clients

  def get_clients(self, capability):
    clients = list()
    for client in self.clients:
      if capability in client['capabilities']:
        clients.append(client)
    return clients

  def restart(self, virgin=False):
    self.socket.send_and_receive({'id': 'root', 'fcn': 'restart', 'virgin': virgin})
  def upgrade(self, virgin=False):
    self.socket.send_and_receive({'id': 'root', 'fcn': 'upgrade', 'virgin': virgin})
  def delStaleClients(self):
    self.socket.send_and_receive({'id': 'root', 'fcn': 'delStaleClients'})
  def startSITL(self, ip):
    self.socket.send_and_receive({'id': 'root', 'fcn': 'launch_sitl', 'client_ip': ip})
  def startDSS(self, ip):
    self.socket.send_and_receive({'id': 'root', 'fcn': 'launch_dss', 'client_ip': ip})
  def start_app(self, app, extra_args=[]):
    self.socket.send_and_receive({'id': 'root', 'fcn': 'launch_app', 'app': app, 'extra_args': extra_args})
  def get_version(self):
    answer = self.socket.send_and_receive({'id': 'root', 'fcn': 'get_info'})
    return answer.get('git_version', 'unknown'), answer.get('git_branch', '???')
  def get_performance(self):
    answer = self.socket.send_and_receive({'id': 'root', 'fcn': 'get_performance'})
    if dss.auxiliaries.zmq.is_ack(answer):
      performance = answer["performance"]
    else:
      performance = "unknown performance..."
    return performance
  def get_processes(self, project):
    answer = self.socket.send_and_receive({'id': 'root', 'fcn': 'get_processes', 'project': project})
    return answer
  def kill_process(self, pid):
    answer = self.socket.send_and_receive({'id': 'root', 'fcn': 'kill_process', 'pid': pid})
    return answer


def check_remote(func):
  @wraps(func)
  def decorated_function(*args, **kwargs):
    remote = Remote.query.filter_by(ip=request.remote_addr).first()
    if remote:
      return func(*args, **kwargs)
    return render_template('403.html')

  return decorated_function

@app.route('/')
@check_remote
def index():
  ip = request.remote_addr
  name = Remote.query.filter_by(ip=ip).first().name
  project = get_project(ip)
  meta = {'name': name, 'project': project, 'page': '/'}
  return render_template('index.html', meta=meta)

@app.route('/clients')
@check_remote
def clients():
  ip = request.remote_addr
  name = Remote.query.filter_by(ip=ip).first().name
  project = get_project(ip)
  try:
    crmMonitor = CRM_Monitor(project)
    crmMonitor.update_clients()
    meta = {'name': name, 'project': project, 'page': 'clients'}
    performance = crmMonitor.get_performance()
    return render_template('clients.html', meta=meta, clients=crmMonitor.clients, performance=performance)
  except:
    return redirect(url_for('index'))

@app.route('/clients/delStaleClients')
@check_remote
def clients_delStaleClients():
  ip = request.remote_addr
  project = get_project(ip)
  crmMonitor = CRM_Monitor(project)
  crmMonitor.delStaleClients()
  return redirect(url_for('clients'))

@app.route('/tasks')
@check_remote
def tasks():
  ip = request.remote_addr
  name = Remote.query.filter_by(ip=ip).first().name
  project = get_project(ip)

  try:
    crmMonitor = CRM_Monitor(project)
    git_version, git_branch = crmMonitor.get_version()
  except Exception:
    return 'crm not responsive, please try again'
  #Ask CRM for process data
  answer = crmMonitor.get_processes(project)
  if dss.auxiliaries.zmq.is_ack(answer):
    processes = answer["processes"]
  else:
    processes = list()
  meta = {'name': name, 'project': project, 'page': 'tasks'}
  performance = crmMonitor.get_performance()

  return render_template('tasks.html', meta=meta, processes=processes, performance=performance, git_branch=git_branch, git_version=git_version)

@app.route('/tasks/kill/<pid>')
def tasks_kill(pid):
  ip = request.remote_addr
  project = get_project(ip)
  try:
    crmMonitor = CRM_Monitor(project)
  except Exception:
    return 'crm not responsive, please try again'
  answer = crmMonitor.kill_process(int(pid))
  if dss.auxiliaries.zmq.is_nack(answer):
    flash(answer['description'], 'error')
  return redirect(url_for('tasks'))

@app.route('/tasks/start_sitl')
@check_remote
def tasks_start_sitl():
  ip = request.remote_addr
  #name = Remote.query.filter_by(ip=ip).first().name
  project = get_project(ip)
  crmMonitor = CRM_Monitor(project)
  crmMonitor.startSITL(ip=request.remote_addr)
  return redirect(url_for('tasks'))

@app.route('/tasks/start_dss')
@check_remote
def tasks_start_dss():
  ip = request.remote_addr
  #name = Remote.query.filter_by(ip=ip).first().name
  project = get_project(ip)
  crmMonitor = CRM_Monitor(project)
  crmMonitor.startDSS(ip=request.remote_addr)
  return redirect(url_for('tasks'))

@app.route('/tasks/app_noise')
@check_remote
def tasks_app_noise():
  ip = request.remote_addr
  #name = Remote.query.filter_by(ip=ip).first().name
  project = get_project(ip)
  crmMonitor = CRM_Monitor(project)
  crmMonitor.start_app("app_noise.py")
  return redirect(url_for('tasks'))

@app.route('/tasks/app_monitor')
@check_remote
def tasks_app_monitor():
  ip = request.remote_addr
  #name = Remote.query.filter_by(ip=ip).first().name
  project = get_project(ip)
  crmMonitor = CRM_Monitor(project)
  crmMonitor.start_app('app_monitor.py', extra_args=["--mqtt_agent"])
  return redirect(url_for('tasks'))

@app.route('/tasks/restart')
@check_remote
def tasks_restart():
  ip = request.remote_addr
  #name = Remote.query.filter_by(ip=ip).first().name
  project = get_project(ip)
  crmMonitor = CRM_Monitor(project)
  crmMonitor.restart()
  return redirect(url_for('tasks'))

@app.route('/tasks/upgrade')
@check_remote
def tasks_upgrade():
  ip = request.remote_addr
  #name = Remote.query.filter_by(ip=ip).first().name
  project = get_project(ip)
  crmMonitor = CRM_Monitor(project)
  crmMonitor.upgrade()
  time.sleep(3)
  return redirect(url_for('tasks'))

@app.route('/selfie', methods=['GET'])
@check_remote
def selfie():
  ip = request.remote_addr
  project = get_project(ip)
  name = Remote.query.filter_by(ip=ip).first().name
  meta = {'name': name, 'project': project, 'page': 'selfie'}

  try:
    crmMonitor = CRM_Monitor(project)
    crmMonitor.update_clients()
    performance = crmMonitor.get_performance()
    if request.method == 'GET':
      if list(filter(lambda key : key["name"]=="app_selfie.py", crmMonitor.clients)):
        return render_template('selfie.html', meta=meta, clients=crmMonitor.clients, performance=performance, app_selfie=True)
      else:
        return render_template('selfie.html', meta=meta, clients=crmMonitor.clients, performance=performance, app_selfie=False)
  except:
    return redirect(url_for('tasks'))

@app.route('/selfie/launch_app', methods=["POST"])
@check_remote
def selfie_launch_app():
  ip = request.remote_addr
  project = get_project(ip)
  name = Remote.query.filter_by(ip=ip).first().name
  meta = {'name': name, 'project': project, 'page': 'selfie'}
  try:
    crmMonitor = CRM_Monitor(project)
    crmMonitor.update_clients()
    if request.method == 'POST':
      if request.form['submit-button'] == "launch_app":
        if len(request.form.getlist('check'))==1:
          crmMonitor.start_app("app_selfie.py",[f"--camera_drone_id={request.form['check']}"])
          return redirect(url_for('selfie'))
        else:
          return redirect(url_for('tasks'))
      return render_template('selfie.html', meta=meta, clients=crmMonitor.clients, app_selfie=False)
  except:
    return redirect(url_for('tasks'))

@app.route('/selfie/follow', methods=["POST"])
@check_remote
def selfie_follow():
  ip = request.remote_addr
  project = get_project(ip)
  name = Remote.query.filter_by(ip=ip).first().name
  meta = {'name': name, 'project': project, 'page': 'selfie'}
  try:
    crmMonitor = CRM_Monitor(project)
    crmMonitor.update_clients()
    if request.method == 'POST':
      if request.form['submit-button'] == "follow":
        app_selfie = list(filter(lambda key : key["name"]=="app_selfie.py", crmMonitor.clients))
        if app_selfie:
          ip = app_selfie[0]['ip']
          port = app_selfie[0]['port']
          socket = dss.auxiliaries.zmq.Req(zmq.Context(), ip=ip, port=port)
          #Check if one other is selected
          if len(request.form.getlist('check'))==1:
            height = request.form.get('height-slider')
            if height:
              #radius =  request.form.get('radius-slider')
              #yaw_rate =  request.form.get('yaw-rate-slider')
              socket.send_and_receive({"fcn": "set_pattern", "id": "GUI", "pattern": "above", "rel_alt": height, "heading": "course"})
            socket.send_and_receive({"fcn": "follow_her", "id": "GUI", "enable": True, "target_id": request.form['check'] })
            return redirect(url_for('selfie'))
          else:
            return redirect(url_for('tasks'))
      return render_template('selfie.html', meta=meta, clients=crmMonitor.clients, app_selfie=False)
  except:
    return redirect(url_for('tasks'))

@app.route('/selfie/release', methods=["POST"])
@check_remote
def selfie_release():
  ip = request.remote_addr
  project = get_project(ip)
  name = Remote.query.filter_by(ip=ip).first().name
  meta = {'name': name, 'project': project, 'page': 'selfie'}
  try:
    crmMonitor = CRM_Monitor(project)
    crmMonitor.update_clients()
    if request.method == "POST":
      app_selfie = list(filter(lambda key : key["name"]=="app_selfie.py", crmMonitor.clients))
      if app_selfie:
        ip = app_selfie[0]['ip']
        port = app_selfie[0]['port']
        socket = dss.auxiliaries.zmq.Req(zmq.Context(), ip=ip, port=port)
        if request.form.get('release') == 'Release':
          socket.send_and_receive({"fcn": "follow_her", "id": "GUI", "enable": False})
          return render_template('selfie.html', meta=meta, clients=crmMonitor.clients)
  except:
    return redirect(url_for('tasks'))

@app.route('/selfie/set_pattern', methods=["POST"])
@check_remote
def selfie_set_pattern():
  ip = request.remote_addr
  project = get_project(ip)
  name = Remote.query.filter_by(ip=ip).first().name
  meta = {'name': name, 'project': project, 'page': 'selfie'}
  try:
    crmMonitor = CRM_Monitor(project)
    crmMonitor.update_clients()
    if request.method == 'POST':
      app_selfie = list(filter(lambda key : key["name"]=="app_selfie.py", crmMonitor.clients))
      if app_selfie:
        ip = app_selfie[0]['ip']
        port = app_selfie[0]['port']
        socket = dss.auxiliaries.zmq.Req(zmq.Context(), ip=ip, port=port)
        if request.form.get('height-slider'):
          height = request.form.get('height-slider')
          radius =  request.form.get('radius-slider')
          yaw_rate =  request.form.get('yaw-rate-slider')
          socket.send_and_receive({"fcn": "set_pattern", "id": "GUI", "pattern": "above", "rel_alt": height, "heading": "course"})
          return render_template('selfie.html', meta=meta, clients=crmMonitor.clients, app_selfie=True, height=height, radius=radius, yaw_rate=yaw_rate)
      return redirect(url_for('selfie'))
  except:
    return redirect(url_for('tasks'))

@app.route('/settings', methods=['GET', 'POST'])
@check_remote
def settings():
  ip = request.remote_addr
  name = Remote.query.filter_by(ip=ip).first().name
  project = get_project(ip)

  form = SettingsForm(request.form)

  remote = Remote.query.filter_by(ip=request.remote_addr).first()
  name = Remote.query.filter_by(ip=request.remote_addr).first().name
  meta = {'name': name, 'project': project, 'page': 'settings'}

  if not form.name.data:
    form.name.data = name

  if form.validate_on_submit():
    flash(f'Name updated for ip {request.remote_addr}: {form.name.data}!', 'info')
    remote.name=form.name.data
    db.session.commit()
    return redirect(url_for('index'))

  return render_template('settings.html', meta=meta, form=form)

@app.route('/ip', methods=['GET'])
def get_my_ip():
  return f'Your ip is {request.remote_addr}'

@app.route('/start')
def start():
  # the "answer" value is stored in the user session
  # the session is sent to the client in a cookie and is not encrypted!
  # python3 -c 'import base64; print(base64.urlsafe_b64decode("eyJhbnN3ZXIiOjE5NSwidHJ5X251bWJlciI6Mn0==="))'
  session['answer'] = random.randint(1, 1000)
  session['try_number'] = 1
  return redirect(url_for('guess'))

@app.route('/guess')
def guess():
  guess_ = int(request.args['guess']) if 'guess' in request.args and request.args.get('guess') else 0
  if request.args.get('guess'):
    if guess_ == session['answer']:
      return render_template('win.html')
    else:
      session['try_number'] += 1
      if session['try_number'] > 3:
        return render_template('lose.html', guess=guess_)
  return render_template('guess.html', try_number=session['try_number'], guess=guess_)

@app.route('/video', methods=['GET'])
def video():
  """Video streaming home page."""
  ip = request.remote_addr
  name = Remote.query.filter_by(ip=ip).first().name
  project = get_project(ip)
  source = request.args.get('source')
  try:
    crmMonitor = CRM_Monitor(project)
    crmMonitor.update_clients()
    video_clients = crmMonitor.get_clients(capability='video')
    meta = {'name': name, 'project': project, 'page': 'video'}
    return render_template('video.html', meta=meta, source=source, clients=video_clients)
  except:
    return redirect(url_for('index'))

def gen(camera):
  """Video streaming generator function."""
  yield b'--frame\r\n'
  while True:
    frame = camera.get_frame()
    yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


@app.route('/video_feed', methods=['GET'])
def video_feed():
  """Video streaming route. Put this in the src attribute of an img tag."""
  source = request.args.get('source')
  camera = Camera("rtsp://localhost:8554/"+source)
  return Response(gen(camera),
                  mimetype='multipart/x-mixed-replace; boundary=frame')

@app.errorhandler(404)
def page_not_found(e):
  # note that we set the 404 status explicitly
  return render_template('404.html'), 404
