FROM ubuntu:latest

RUN apt-get update && \
    apt-get -y install sudo

CMD tail -f /dev/null