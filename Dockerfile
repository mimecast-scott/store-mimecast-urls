FROM python:3-slim
LABEL maintainer="s@mck.la"
ARG MY_APP_PATH=/opt/store-mimecast-urls

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ntp supervisor \
    && mkdir -p ${MY_APP_PATH}/data

ADD decodeapi.py main.py auth.py requirements.txt ${MY_APP_PATH}
ADD store-mimecast-urls.conf /etc/supervisor/conf.d/
ADD decode-mimecast-api.conf /etc/supervisor/conf.d/
ADD supervisor.conf /etc/supervisor/supervisord.conf

#COPY data ${MY_APP_PATH}/data
RUN pip install -r ${MY_APP_PATH}/requirements.txt
# -r ${MY_APP_PATH}/requirements.txt
#RUN pip3 install fastapi uvicorn[standard] qrcode[pil] requests
WORKDIR ${MY_APP_PATH}


VOLUME [${MY_APP_PATH}]

ENTRYPOINT ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
#ENTRYPOINT ["python","-u","main.py"]

EXPOSE 8000/tcp 9001/tcp
