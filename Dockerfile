FROM tiangolo/uwsgi-nginx-flask:python3.8
COPY ./requirements.txt /var/www/requirements.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r /var/www/requirements.txt
COPY ./app /app