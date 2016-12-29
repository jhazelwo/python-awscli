FROM ubuntu:16.04
MAINTAINER "John Hazelwood" <jhazelwo@users.noreply.github.com>
RUN apt-get clean && \
  apt-get -y update && \
  apt-get -y upgrade && \
  apt-get -y install python3-yaml python3 python3-pip bash-completion vim groff-base curl less time && \
  pip3 install --upgrade awscli pip python-dateutil fileasobj && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /var/cache/*
RUN install -d -m 0700 -o 1000 -g 1000 /aws && \
  groupadd --gid 1000 human && \
  useradd --uid 1000 --gid 1000 --home-dir /aws/home -M --shell /bin/bash human
WORKDIR /aws
USER human
ENTRYPOINT ["/bin/bash", "--login"]
