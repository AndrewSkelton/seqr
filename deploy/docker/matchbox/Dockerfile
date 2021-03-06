FROM openjdk:8-jdk

RUN apt-get update \
 && apt-get install -y wget \
 && apt-get install -y git \
 && apt-get install -y maven \
 && apt-get install -y python \
 && apt-get install -y gcc  \
 && apt-get install -y python-dev \
 && apt-get install -y python-setuptools \
 && /usr/bin/easy_install -U pip \
 && /usr/local/bin/pip install crcmod 

MAINTAINER MacArthur Lab

ADD settings.xml /root/.m2/settings.xml
ADD entrypoint.sh  /root/bin/entrypoint.sh

env MVN=mvn

#first get Exomiser built in the local maven for matchbox to import in
#---------------------------------------------------------------------------

RUN git clone -b development https://github.com/exomiser/Exomiser
WORKDIR Exomiser
RUN $MVN clean install package

#now matchbox (and it will see Exomisor in local maven repo)
#---------------------------------------------------------------------------

RUN git clone https://github.com/macarthur-lab/matchbox
WORKDIR matchbox
RUN $MVN -Dmaven.test.skip=true clean install package

env MATCHBOX_JAR=/Exomiser/matchbox/target/matchbox-0.1.0.jar
env MATCHBOX_CONFIG_DIR=/Exomiser/matchbox/config


#Now get support data for Exomiser models (for now, cpying, switch with wget)
#-----------------------------------------------------

#----first get gsutils to interface with google
RUN wget https://storage.googleapis.com/pub/gsutil.tar.gz \
 && mkdir /root/gsutils_dir \
 && tar xfz gsutil.tar.gz -C /root/gsutils_dir \
 && rm gsutil.tar.gz \
 && export PATH=${PATH}:/root/gsutils_dir/gsutil

#----now get the data and untar it

WORKDIR data
RUN /root/gsutils_dir/gsutil/gsutil -m -o GSUtil:parallel_composite_upload_threshold=150M cp gs://seqr-hail/reference_data/exomiser/data.tar.gz data.local.tar.gz \
 && tar -xzf data.local.tar.gz \
 && rm data.local.tar.gz \
 && pwd \
 && ls -l


#Now set matchbox up for deployment and copy over jar and config files
#---------------------------------------------------------------------------
WORKDIR /matchbox_deployment
RUN cp -rf $MATCHBOX_CONFIG_DIR . \
 && cp $MATCHBOX_JAR .


EXPOSE 9020

CMD ["/root/bin/entrypoint.sh"]
