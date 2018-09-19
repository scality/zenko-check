from .util import WatchProcess
import subprocess
from functools import partial
import re

FORWARDED_PORTS = {}

PF_TMPL = 'kubectl port-forward {pod} {namespace} {local}:{remote}'
LIST_PODS = 'kubectl get pods --all-namespaces -o=jsonpath="{.items[*].metadata.name}"'

MONGO_REGEX = r'.*mongodb.*'
TILLER_REGEX = r'.*tiller.*'


def auto_forward(mongo = False, tiller = False, use_ctx = False):
	def outer(f):
		def inner(ctx, *args, **kwargs):
			close_mongo = False
			close_tiller = False
			conf = ctx
			if use_ctx: # To handle pass_context and pass_obj
				conf = ctx.obj
			if conf.auto_forward and mongo:
				mongo_pf = forward_mongodb() # Returns an existing PortForward if any
				close_mongo = mongo_pf.open() # Returns True if port has not been opened / False If its already open
			if conf.auto_forward and tiller:
				tiller_pf = forward_tiller()
				close_tiller = tiller_pf.open()
			ret = f(ctx, *args, **kwargs)
			if close_mongo:
				mongo_pf.close()
			if close_tiller:
				tiller_pf.close()
			return ret
		return inner
	return outer


class PortForward:
	def __init__(self, pattern, remote, local=None, namespace=None):
		self._pattern = pattern
		self._remote = remote
		self._local = local if local is not None else remote
		self._namespace = '--namespace %s'%namespace if namespace is not None else ''
		self._pod_name = None
		self._proc = None

	@staticmethod
	def list_pods():
		resp = WatchProcess(LIST_PODS, stdout=subprocess.PIPE)().communicate()
		return str(resp[0]).replace("'", '').split(' ')

	@property
	def pod(self):
		if self._pod_name is not None:
			return self._pod_name
		for pod in self.list_pods():
			if re.search(self._pattern, pod):
				self._pod_name = pod
				return pod

	def open(self):
		if self._proc is None:
			self._proc = WatchProcess(PF_TMPL.format(
				pod=self.pod,
				namespace=self._namespace,
				local=self._local,
				remote=self._remote),
				stdout=subprocess.DEVNULL,
				stderr=subprocess.DEVNULL)
			return True
		return False

	def close(self):
		if self._proc is not None:
			self._proc.terminate()
			return True
		return False


def forward_pod(pattern, port, local = None, namespace = None):
	if pattern in FORWARDED_PORTS:
		return FORWARDED_PORTS[pattern]
	pf = PortForward(pattern, port, local=local, namespace=namespace)
	FORWARDED_PORTS[pattern] = pf
	return pf


def get_port_forward(pattern = None):
	if pattern is None:
		return list(FORWARDED_PORTS.items())
	return FORWARDED_PORTS.get(pattern, None)


forward_mongodb = partial(forward_pod, MONGO_REGEX, 27017, 40420)
forward_tiller = partial(forward_pod, TILLER_REGEX, 44134, 40421, namespace = 'kube-system')
