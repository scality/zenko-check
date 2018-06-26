FROM python:3.6-alpine

ENV HELM_VERSION 2.9.1
ENV ZENKO_CHECK_VER 0.1.1
ADD https://storage.googleapis.com/kubernetes-helm/helm-v${HELM_VERSION}-linux-amd64.tar.gz /tmp/helm.tar.gz

RUN pip install zenko-check==${ZENKO_CHECK_VER} \
	&& tar xzf /tmp/helm.tar.gz -C /tmp \
	&& cp /tmp/linux-amd64/helm /usr/bin \
	&& chmod +x /usr/bin/helm \
	&& rm /tmp/helm.tar.gz

ENTRYPOINT [ "zenko-check" ]

CMD ["help"]
