#!/bin/sh
set -e

if [ -z "$1" ]; then
	echo "You must specify major, minor, or patch"
	exit 1
fi

which bumpversion > /dev/null
if [ "$?" -eq "1" ]; then
	echo "bumpversion is not installed or not currently on the path"
	exit 1
fi

echo "Bumping $1"
VER=$(bumpversion --list "$1" | grep new_version | cut -d '=' -f 2)
MAJOR=$(echo "$VER" | cut -d '.' -f 1)
MINOR=$(echo "$VER" | cut -d '.' -f 2)

echo "Removing old releases"
rm -rf dist/

echo "Building sdist and bdist"
python setup.py sdist

echo "Building zenko/zcheck:$VER"
echo "Will also tag zenko/zcheck:$MAJOR, zenko/zcheck:$MAJOR.$MINOR, and zenko/zcheck:latest"

docker build -t zenko/zcheck:$VER .
docker tag zenko/zcheck:$VER zenko/zcheck:$MAJOR
docker tag zenko/zcheck:$VER zenko/zcheck:$MAJOR.$MINOR
docker tag zenko/zcheck:$VER zenko/zcheck:latest

echo "Pushing docker images"
docker push zenko/zcheck:$VER
docker push zenko/zcheck:$MAJOR
docker push zenko/zcheck:$MAJOR.$MINOR
docker push zenko/zcheck:latest

echo "Uploading to PyPi"
twine upload dist/*

echo "Pushing to repo"
git push
git push --tags
