FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN apt-get update

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ADD requirements.txt /usr/src/app/
RUN pip install -r requirements.txt
ADD . /usr/src/app/

CMD ["tail", "-f", "/dev/null"]