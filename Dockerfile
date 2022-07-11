FROM python:3.8

ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

RUN apt-get update && apt-get install -y netcat
RUN pip install --upgrade pip

RUN pip install --upgrade pip
COPY requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8000

COPY . /code/

RUN mkdir -p /root/.config/ptpython
COPY ptpython-config.py /root/.config/ptpython/config.py

COPY ./runserver.sh /
RUN chmod +x /runserver.sh

COPY ./entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]