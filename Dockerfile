FROM ubuntu:latest

RUN apt-get update && \
    apt-get -y install sudo

CMD ["sudo" , "cat", "/etc/passwd"]