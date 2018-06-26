from . import log

log.setupLogging('zenko_check',
	level = log.ERROR,
	blacklist = [
		'azure.storage.common.storageclient'
	])

__version__ = '0.0.3'


from .cli import zenko_check
def entry():
	zenko_check()
