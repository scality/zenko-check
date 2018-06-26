# zenko-check

## Usage

zenko-check is a command line utility to check configuration and diagnose problems with a production Zenko deployment.

## Prerequisites

zenko-check requires [helm](https://github.com/kubernetes/helm) to be installed and be configured to be able to access tiller running inside kubernetes.

## Installation

zenko-check can be installed directly from Pypi using pip:

```
pip install zenko-check
```

a docker images is also provided for convenience

```
docker pull zenko/zenko-check:latest
docker run -it zenko/zenko-check help
```

## Global Options and Flags

```
--mongo 		Override the default mongo connection string (host:port)
--helm-release, -r	The helm release name Zenko was installed under.
```

## Subcommands

### checkup
###### Run all checks and tests (warning this could take a while)

### k8s
###### Checks kubernetes related configuration


```
--check-services, -c 	Attempt to connect to defined services and report their status.

```

### orbit
###### Check overlay configuration applied via orbit

### backends
###### Check existence and configuration of backend buckets



```
-d, --deep  	Enable deep checking. Check every Zenko bucket for its backing bucket
            	(same as zenko-check buckets)
```

### buckets
###### Check every Zenko bucket for its respective backend bucket
