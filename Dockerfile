FROM python:3.6-alpine

ENV HELM_VERSION 2.9.1
ENV KUBECTL_VERSION 1.11.0
ENV ZENKO_CHECK_VER 0.1.1

ADD https://storage.googleapis.com/kubernetes-helm/helm-v${HELM_VERSION}-linux-amd64.tar.gz /tmp/helm.tar.gz
ADD https://storage.googleapis.com/kubernetes-release/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl /usr/bin/

ADD ./requirements.txt /tmp
RUN apk add --update build-base libffi-dev openssl-dev \
	&& pip install -r /tmp/requirements.txt \
	&& tar xzf /tmp/helm.tar.gz -C /tmp \
	&& cp /tmp/linux-amd64/helm /usr/bin \
	&& chmod +x /usr/bin/helm \
	&& rm /tmp/helm.tar.gz \
	&& chmod +x /usr/bin/kubectl \
	&& apk del build-base

COPY . /app
RUN cd /app \
	&& python setup.py install

ENTRYPOINT [ "/app/entrypoint.sh" ]

CMD ["help"]
