FROM python:3

ENV DOCKER_BUCKET get.docker.com
ENV DOCKER_VERSION 1.13.1
ENV DOCKER_SHA256 97892375e756fd29a304bd8cd9ffb256c2e7c8fd759e12a55a6336e15100ad75

RUN set -x \
    && curl -fSL "https://${DOCKER_BUCKET}/builds/Linux/x86_64/docker-${DOCKER_VERSION}.tgz" -o docker.tgz \
    && echo "${DOCKER_SHA256} *docker.tgz" | sha256sum -c - \
    && tar -xzvf docker.tgz \
    && mv docker/* /usr/local/bin/ \
    && rmdir docker \
    && rm docker.tgz \
    && docker -v

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY /runner.py /runner.py

RUN mkdir -p /root/.ssh \
    && chmod 700 /root/.ssh \
    && ssh-keyscan github.com >> /root/.ssh/known_hosts \
    && ssh-keyscan bitbucket.org >> /root/.ssh/known_hosts

RUN curl -fL "https://raw.githubusercontent.com/buildkite/docker-ssh-env-config/d06f20bdc7457a647bfe3724d94525f83c863091/ssh-env-config.sh" -o /usr/local/bin/ssh-env-config.sh \
    && chmod +x /usr/local/bin/ssh-env-config.sh 

RUN curl -fL "https://gist.githubusercontent.com/undernewmanagement/8f7cad8bcd3dfc6435769a1ec0a7e342/raw/eebe9fdf400bf4a8f44c960cc0d81fddc6a8839d/semver.sh" -o /usr/local/bin/semver.sh \
    && chmod +x /usr/local/bin/semver.sh 

EXPOSE 5000 4444

ENTRYPOINT ["ssh-env-config.sh"]
