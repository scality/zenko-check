


ORBIT_ERROR_MSG = 'This probably means that Cloudserver is having difficulty communicating with Orbit.'

class ZCheckBaseException(Exception):
	def __init__(self, *args, **kwargs):
		super().__init__(self._msg_tmpl.format(*args, **kwargs))


class RequiredBinaryException(ZCheckBaseException):
	_msg_tmpl = 'No binary name {} found in PATH\nYou must have {} installed to use this tool!\nPlease make sure {} is installed and available in you PATH'
	def __init__(self, cmd):
		super().__init__(*([cmd]*3))

class MongoConnectionError(ZCheckBaseException):
	_msg_tmpl = 'Unable to connect to mognodb at {}!'

class DBNotFoundException(ZCheckBaseException):
	_msg_tmpl = 'Unable to find {} database in mongodb!'

class CollectionNotFoundException(ZCheckBaseException):
	_msg_tmpl = 'Unable to find collection {} in db {} in mognodb!'

class NoOverlayConfigException(ZCheckBaseException):
	_msg_tmpl = 'No overlay configuration found!\n' + ORBIT_ERROR_MSG

class InvalidOverlayConfigVersionException(ZCheckBaseException):
	_msg_tmpl = 'Could not find overlay version {}\n' + ORBIT_ERROR_MSG

class NoOverlayPrivateKeyException(ZCheckBaseException):
	_msg_tmpl = 'Could not find Zenkos private key to access secrets!\n' + ORBIT_ERROR_MSG
