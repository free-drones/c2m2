FROM tiangolo/uwsgi-nginx-flask:python3.9

WORKDIR /git
RUN git clone https://github.com/free-drones/rise_drones.git
WORKDIR /python_requirements
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/git/rise_drones/src/"
WORKDIR /app
