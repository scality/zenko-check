from boto3 import Session
import botocore
from botocore.handlers import set_list_objects_encoding_type_url
from azure.storage.blob import BlockBlobService


class AzureClientError(Exception):
	def __init__(self, error):
		self._error = error

	@property
	def response(self):
		return dict(Error=dict(Code=self._error))

class ObjectStub:
	def __init__(self, k, v = None):
		def func(*args, **kwargs):
			pass
		setattr(self, k, v if v is not None else func)

class AzureResource:
	def __init__(self, service):
		self._service = service

	def Bucket(self, name):
		return AzureBucket(self._service, name)

	def resource(self, *args, **kwargs):
		return self

	@property
	def meta(self):
		os = ObjectStub('head_bucket', self._head_bucket)
		return ObjectStub('client', os)

	def _head_bucket(self, Bucket = None):
		if self._service.exists(Bucket):
			return True
		raise AzureClientError('404')

class AzureBucket:
	def __init__(self, service, name):
		self._service = service
		self._name = name

	@property
	def name(self):
		return self._name

	def create(self):
		return self._service.create_container(self._name)

	def delete(self):
		return self._service.delete_container(self._name)

	def put_object(self, Key = None, Body = None):
		if Key is None or Body is None:
			raise Exception
		return self._service.create_blob_from_bytes(
			self._name,
			Key,
			Body
		)

	def download_fileobj(self, key, f):
		blob = self._service.get_blob_to_bytes(
			self._name,
			key
		)
		if blob:
			f.write(blob.content)
			return True
		else:
			raise Exception('Failed to get blob %s/%s from azure!'%(self._name, key))

	@property
	def objects(self):
		def f():
			return self._service.list_blobs(self._name)
		return ObjectStub('all', f)

	def Versioning(self):
		return ObjectStub('suspend')

	def  delete_blob(self, name):
		self._service.delete_blob(self._name, name, delete_snapshots = True)



def _build_aws(backend):
	return Session(aws_access_key_id = backend.access_key,
					aws_secret_access_key = backend.secret_key)

def _build_gcp(backend):
	sesh = _build_aws(backend)
	sesh.events.unregister('before-parameter-build.s3.ListObjects', set_list_objects_encoding_type_url)
	return sesh

def _build_azure(backend):
	return AzureResource(
			BlockBlobService(
				account_name = backend.access_key,
				account_key = backend.secret_key
			)
		)

BUILDERS = {
	'GCP': _build_gcp,
	'AZURE': _build_azure
}

def build_client(backend):
	sesh = BUILDERS.get(backend.type, _build_aws)(backend)
	if backend.endpoint == 'None':
		endpoint = None
	else:
		endpoint = 'https://%s'%backend.endpoint
	return sesh.resource('s3', endpoint_url=endpoint)


class BackendWrapper:
	def __init__(self, backend):
		self._backend = backend
		self.builtin = self._backend.type == 'FILE' or self._backend.type == 'MEM'
		if not self.builtin:
			self._client = build_client(backend)
		self._mine = None

	@property
	def name(self):
		return self._backend.name

	@property
	def bucket(self):
		return self._backend.bucket

	@property
	def exists(self):
		if self.builtin:
			return True
		try:
			self._client.meta.client.head_bucket(Bucket = self._backend.bucket)
			self._mine = True
			return True
		except (botocore.exceptions.ClientError, AzureClientError) as e:
			error_code = int(e.response['Error']['Code'])
			if error_code == 403:
				self._mine = False
				return True
			elif error_code == 404:
				return False

	@property
	def mine(self):
		if self.builtin:
			return True
		if self._mine is None:
			if self.exists:
				return self._mine
			return False
		return self._mine

	@property
	def versioned(self):
		pass

def build_backends(backends):
	for backend in backends:
		yield BackendWrapper(backend)
