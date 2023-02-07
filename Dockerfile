FROM tiangolo/uwsgi-nginx-flask:python3.9
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --no-cache-dir -r requirements.txt
