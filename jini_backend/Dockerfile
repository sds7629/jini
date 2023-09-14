FROM python:3.11

## Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get -y update

RUN mkdir /jiniserver
ADD . /jiniserver
WORKDIR /jiniserver

RUN python -m pip install --upgrade pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# EXPOSE 8000
# 컨테이너가 수행될 때 entrypoint가 실행
ENTRYPOINT ["sh", "./entrypoint.sh"]