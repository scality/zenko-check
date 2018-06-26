from threading import Thread, Event
import os
import os.path
import subprocess
import shlex
import click

MONGO_BASE_HOST = 'mongodb-replicaset'

def which(name):
	for path in os.getenv("PATH").split(os.path.pathsep):
		full_path = path + os.sep + name
		if os.path.exists(full_path):
			return True
	return False

def complain_no_cmd(cmd, exit = True):
	click.secho('''No binary name %s found in PATH
You must have %s installed to use this tool!
Please make sure %s is installed and available in you PATH'''%tuple([cmd]*3),
	fg='red', bold=True)
	sys.exit(1)

def check_cmd(cmd):
	if not which(cmd):
		complain_no_cmd(cmd)

class WatchedProcess(Thread):
	"""
		A light wrapper around a Popen object
		all args are passed through to the Popen constructor
		2 additional keyword arguments are added
			on_exit
			on_error
		These should contain a callable object taking 1 arguement return_code
		on_exit will always be called when the process exits
		on_error will be called when the process exits with return_code != 0
	"""

	def __init__(self, *args, on_exit = None, on_error = None, **kwargs):
		super().__init__()
		self.daemon = True
		self._proc = None
		self._started = Event()
		self._args = args
		self._kwargs = kwargs
		self._on_exit = on_exit
		self._on_error = on_error
		self._proc = subprocess.Popen(*self._args, **self._kwargs)

	def __call__(self):
		"""for convenience return the popen object when called"""
		return self._proc

	def run(self):
		self._started.set()
		self._proc.wait()
		rc = self._proc.returncode
		if self._on_exit:
			self._on_exit(rc)
		if self._on_error and rc != 0:
			self._on_error(rc)

	def terminate(self):
		return self._proc.terminate()

	def kill(self):
		return self._proc.kill()

	@property
	def status(self):
		if self._proc:
			return self._proc.poll()

	def wait(self):
		self._started.wait()
		return self._proc.wait() if self._proc else None


def WatchProcess(cmd, start = True, **kwargs):
	wp = WatchedProcess(shlex.split(cmd), **kwargs)
	if start:
		wp.start()
	return wp

def mark_last(it):
	if not hasattr(it, '__next__'):
		it = iter(it)
	try:
		value = next(it)
	except StopIteration:
		pass
	else:
		for v in it:
			yield False, value
			value = v
		yield True, value
