FROM python:3.7-alpine3.8

# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.8/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.8/community" >> /etc/apk/repositories

# install chromedriver
RUN apk update
RUN apk add chromium chromium-chromedriver

RUN apk add xvfb x11vnc fluxbox xdpyinfo st vim terminus-font \
	&& sed -r -i "s/\[exec\] \(xterm\) \{xterm\}/\[exec\] \(st\) \{st -f 'xos4 Terminus-14'\}/" /usr/share/fluxbox/menu \
	&& [[ ! -d /opt ]] && mkdir /opt \
	&& rm -vrf /var/cache/apk/*
    
# upgrade pip
RUN pip install --upgrade pip


ENV APP_HOME /usr/src/app
WORKDIR /$APP_HOME
COPY . $APP_HOME/

RUN pip install -r requirements.txt

CMD tail -f /dev/null