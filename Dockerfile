FROM tiangolo/uwsgi-nginx-flask:python3.9
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
