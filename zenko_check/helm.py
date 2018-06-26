from .util import WatchProcess, check_cmd
import subprocess
import socket
import click

class Service:
	_headings = ('HOSTNAME', 'CLUSTER IP', 'PORTS', 'AGE', 'STATUS')
	_heading_color = 'cyan'

	def __init__(self, line, check = False):
		self._ports = []
		self._check = check
		self._parse_line(line)

	def _parse_line(self, line):
		parts = [p for p in line.split() if p]
		self._host = parts[0]
		self._ip = parts[2]
		for p in parts[4].split(','):
			port, proto = p.split('/')
			self._ports.append((port, proto))
		self._age = parts[5]

	@property
	def endpoints(self):
		for p in self.ports:
			yield self._host, p

	@property
	def ports(self):
		for port, type in self._ports:
			yield port

	@property
	def pports(self):
		return ','.join('/'.join(pair) for pair in self._ports)

	@property
	def ip(self):
		return self._ip

	@property
	def age(self):
		return self._age

	@property
	def repr(self):
		if self._check:
			return self._host, self._ip, self.pports, self._age, ('UP', 'green') if self.check() else ('DOWN', 'red')
		return self._host, self._ip, self.pports, self._age

	def headings(self):
		if self._check:
			return tuple((c, Service._heading_color) for c in Service._headings)
		return tuple((c, Service._heading_color) for c in Service._headings[:-1])

	def check(self):
		up = True
		for ep in self.endpoints:
			try:
				s = socket.create_connection(ep)
			except Exception as e:
				click.secho('Failed to connect to tcp://%s:%s with error %s'%(*ep, e), fg='red')
				up = False
		return up

class Pod:
	_headings = ('NAME', 'READY', 'RESTARTS', 'AGE', 'STATUS')
	_heading_color = 'cyan'
	def __init__(self, line):
		self._parse_line(line)

	def _parse_line(self, line):
		parts = [p for p in line.split() if p]
		self._name = parts[0]
		self._ready = parts[1]
		self._status = parts[2]
		self._restarts = parts[3]
		self._age = parts[4]

	@property
	def name(self):
		return self._name

	@property
	def ready(self):
		return tuple(int(i) for i in self._ready.split('/'))

	@property
	def status(self):
		return self._status

	@property
	def restarts(self):
		return int(self._restarts)

	@property
	def age(self):
		return self._age

	@property
	def repr(self):
		return self.name, self._ready, self._restarts, self._age, (self._status, 'green' if self._status == 'Running' else 'red')

	@classmethod
	def headings(cls):
		return tuple((c, cls._heading_color) for c in cls._headings)



class Status:
	def __init__(self, release, check_pods = False, check_services = False):
		self._release = release
		self._services = []
		self._pods = []
		self._check_pods = check_pods
		self._check_services = check_services
		check_cmd('helm')

	def _helm_status(self):
		proc = WatchProcess('helm status %s'%self._release, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		proc.wait()
		raw = proc().stdout.readlines()
		lines = [x.decode('utf-8').strip() for x in raw]
		return lines

	def _parse_services(self, lines):
		for line in lines:
			self._services.append(Service(line, check = self._check_services))

	def _parse_pods(self, lines):
		for line in lines:
			self._pods.append(Pod(line))

	def _parse(self, lines):
		section_ids = {
			'v1/Service': self._parse_services,
			'v1/Pod': self._parse_pods
		}
		for i, line in enumerate(lines):
			seg = line.replace('==> ', '').replace('(related)', '')
			if seg in section_ids:
				for ei, eline in enumerate(lines[i + 1:]):
					if not eline:
						end = ei + i
						break
				section_ids[seg](lines[i + 2:end + 1])

	def pull_status(self):
		lines = self._helm_status()
		self._parse(lines)

	@property
	def repr(self):
		services = [self._services[0].headings()] + [s.repr for s in self._services]
		pods = [Pod.headings()] + [p.repr for p in self._pods]
		return dict(services=services, pods=pods)
