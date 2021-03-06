FROM python:2.7.11

MAINTAINER MacArthur Lab

# install dependencies of generate_pedigree_images command which generates static images using HaploPainter.pl
RUN apt-get update \
    && apt-get install -y perl build-essential libcairo2-dev libgtk2.0-dev libglib2.0-bin libglib2.0-0 libpango1.0-dev

RUN wget https://raw.github.com/miyagawa/cpanminus/master/cpanm -O /usr/bin/cpanm \
    && chmod +x /usr/bin/cpanm \
    && cpanm --notest Cairo DBI Gtk2 Tk Sort::Naturally

# install utilities for accessing the database, debugging, etc.
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6 \
    && echo "deb http://repo.mongodb.org/apt/debian jessie/mongodb-org/3.4 main" | tee /etc/apt/sources.list.d/mongodb-org-3.4.list \
    && apt-get update \
    && apt-get install -y mongodb-org-tools mongodb-org-shell

RUN apt-get install -y postgresql postgresql-client

RUN apt-get install -y xterm vim emacs nano

RUN apt-get install -y git

# update seqr repo
# DISABLE_CACHE work-around to force git pull on every docker build, based on https://github.com/docker/docker/issues/1996
ARG DISABLE_CACHE=1

RUN git clone -q https://github.com/macarthur-lab/seqr

WORKDIR /seqr

# install seqr dependencies
RUN pip install --upgrade pip gunicorn \
    && pip install --upgrade -r requirements.txt

ENV PYTHONPATH=/seqr:/seqr_settings

COPY shared/config/*.py /seqr_settings/

EXPOSE 8000

COPY shared/gitconfig /root/.gitconfig
COPY shared/config/*.py /seqr_settings/
COPY shared/bin/*.sh /usr/local/bin/
COPY shared/bashrc /root/.bashrc

COPY gcloud/bashrc_custom /root/.bashrc_custom
COPY gcloud/entrypoint.sh /

WORKDIR /seqr

CMD [ "/entrypoint.sh" ]
