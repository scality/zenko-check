from .s3 import build_backends
import click
from .bucket import UserBuckets


def check_backends(overlay, verbose = False):
	yield overlay.headings('backend_check')
	for backend in build_backends(overlay.backends):
		if backend.builtin and verbose:
			yield backend.name, backend.bucket, ('Builtin', 'magenta'), ('Builtin', 'magenta')
			continue
		exists = ('True', 'green') if backend.exists else ('False', 'red')
		mine = ('True', 'green') if backend.mine else ('False', 'red')
		if not backend.exists or not backend.mine or verbose:
			yield backend.name, backend.bucket, exists, mine

def check_buckets(overlay, buckets, verbose = False):
	backends = {b.name: b.exists for b in build_backends(overlay.backends)}
	yield tuple([(x, 'cyan') for x in ['NAME', 'BACKEND', 'OWNER', 'TRANSIENT', 'VALID']])
	for bucket in buckets:
		if not bucket.deleted:
			valid = ('True', 'green') if bucket.location in backends and backends[bucket.location] else ('False', 'red')
			if not bucket.location in backends or not backends[bucket.location] or verbose:
				yield bucket.name, bucket.location, bucket.owner, bucket.transient, valid

def check_bucket_users(overlay, buckets, verbose = False):
	pass
