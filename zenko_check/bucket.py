from pymongo import MongoClient, errors
from .util import MONGO_BASE_HOST

class UserBuckets:
	def __init__(self, helm_release = None, mongo = None):
		if mongo is None:
			if helm_release is None:
				raise Exception('You must provide either monge or helm_release!')
			self._host ='%s-%s'%(helm_release, MONGO_BASE_HOST)
		else:
			self._host = mongo
		self._client = self._build_client(self._host)

	def _build_client(self, host):
		return MongoClient(host,
			connectTimeoutMS = 5000,
			serverSelectionTimeoutMS = 5000)

	def _pull_buckets(self):
		try:
			if not 'metadata' in self._client.database_names():
				# log_err('"metadata" collection not found in mongo!')
				sys.exit(1)
			db = self._client['metadata']
			if not '__usersbucket' in db.collection_names():
				sys.exit(1)
			col = db['__usersbucket']
			for bucket in col.find():
				yield bucket['_id'].split('..|..')[1]
		except errors.ServerSelectionTimeoutError:
			# log_err('Unable to connect to mongo!')
			sys.exit(1)

	@property
	def buckets(self):
		for name in self._pull_buckets():
			yield ZenkoBucket(self._client, name)


class ZenkoBucket:
	def __init__(self, client, name):
		self._name = name
		self._pulled = False
		self._client = client

	def _pull_info(self):
		if not self._pulled:
			try:
				if not 'metadata' in self._client.database_names():
					# log_err('"metadata" collection not found in mongo!')
					sys.exit(1)
				db = self._client['metadata']
				if not '__metastore' in db.collection_names():
					# log_err('No collection named PENSIEVE in metadata')
					sys.exit(1)
				col = db['__metastore']
				bucket = col.find_one({ '_id': self._name})
				if not bucket:
					# Could not find bucket collection
					sys.exit(1)
				self._pulled = True
				self._parse_bucket(bucket['value'])
			except errors.ServerSelectionTimeoutError:
				# log_err('Unable to connect to mongo!')
				sys.exit(1)

	def _parse_bucket(self, data):
		self._name = data['name']
		self._owner = data['ownerDisplayName']
		self._transient = data['transient']
		self._deleted = data['deleted']
		self._location = data['locationConstraint']
		self._created = data['creationDate']

	@property
	def name(self):
		self._pull_info()
		return self._name

	@property
	def owner(self):
		self._pull_info()
		return self._owner

	@property
	def created(self):
		self._pull_info()
		return self._created

	@property
	def transient(self):
		self._pull_info()
		return str(self._transient)

	@property
	def deleted(self):
		self._pull_info()
		return self._deleted

	@property
	def location(self):
		self._pull_info()
		return self._location

def build_buckets(mongo, bkts):
	for b in bkts:
		yield ZenkoBucket(mongo, b)
