#!/bin/sh

if [ ! -z "$KUBECONFIG" ]; then
	echo "$KUBECONFIG" > /kube.conf
	export KUBECONFIG=/kube.conf
fi

if [ -f /kube.conf ]; then
	export KUBECONFIG=/kube.conf
fi

exec zcheck $@
