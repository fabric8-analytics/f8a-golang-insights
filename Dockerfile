FROM centos:7

LABEL maintainer="Avishkar Gupta <avgupta@redhat.com>"

COPY ./insights_engine /insights_engine
COPY ./requirements.txt /requirements.txt

RUN yum install -y epel-release &&\
    yum install -y gcc-c++ git python34-pip python34-requests httpd httpd-devel python34-devel &&\
    yum clean all

RUN chmod 0777 /insights_engine/scripts/entrypoint.sh

RUN pip3 install -r requirements.txt

ENTRYPOINT ["/insights_engine/scripts/entrypoint.sh"]
