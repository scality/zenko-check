from .s3 import build_backends
import click
from .bucket import UserBuckets


def check_backends(overlay, verbose = False):
	yield overlay.headings('backend_check')
	for backend in build_backends(overlay.backends):
		transient = ('True', 'green') if backend.transient else 'False'
		if backend.builtin and verbose:
			yield backend.name, backend.bucket, transient, ('Builtin', 'magenta'), ('Builtin', 'magenta')
			continue
		if backend.exists is True:
			exists = ('True', 'green')
		elif backend.exists is False:
			exists = ('False', 'red')
		else:
			exists = ('----', 'yellow')
		# mine = ('True', 'green') if backend.mine is True else ('False', 'red')
		if backend.mine is True:
			mine = ('True', 'green')
		elif backend.mine is None:
			mine = ('----', 'yellow')
		else:
			mine = ('False', 'red')
		if not backend.exists or not backend.mine or verbose:
			yield backend.name, backend.bucket, transient, exists, mine

def check_buckets(overlay, buckets, verbose = False):
	backends = {b.name: b.exists for b in build_backends(overlay.backends)}
	transient_backends = [b.name for b in overlay.backends if b.transient]
	yield tuple([(x, 'cyan') for x in ['NAME', 'BACKEND', 'OWNER', 'TRANSIENT', 'VALID']])
	for bucket in buckets:
		if not bucket.deleted:
			valid = ('True', 'green') if bucket.location in backends and backends[bucket.location] else ('False', 'red')
			if not bucket.location in backends or not backends[bucket.location] or verbose:
				yield bucket.name, bucket.location, bucket.owner, str(bucket.location in transient_backends), valid

def check_bucket_users(overlay, buckets, verbose = False):
	pass
