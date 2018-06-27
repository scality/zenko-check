zcheck
===========

zcheck is a command-line utility to check the configuration of a
production Zenko deployment and diagnose problems in it.

Pre-Requisites
--------------

zcheck requires a `Helm <https://github.com/kubernetes/helm>`__
installation that is configured to access Tiller running inside
Kubernetes.

Installation
------------

zcheck can be installed directly from PyPi using Pip:

::

    pip install zcheck

A Docker image is also provided for convenience.

::

    docker pull zenko/zcheck:latest
    docker run -it zenko/zcheck help

Syntax
------

zcheck commands conform to the following syntax:

::

    zcheck <global option> <subcommand> <-flag or --verbose_option> <optional target>

Global Options
~~~~~~~~~~~~~~

::

        --mongo  Override the default Mongo connection string (host:port)
    -r, --helm-release   The Helm release name under which Zenko was installed.

Subcommands
~~~~~~~~~~~

checkup
^^^^^^^

Run all checks and tests (may take a while).

k8s
^^^

Check Kubernetes-related configuration.

::

    -c, --check-services    Attempt to connect to defined services and report their status.

orbit
^^^^^

Check overlay configuration applied via Orbit.

backends
^^^^^^^^

Check existence and configuration of backend buckets.

::

    -d, --deep  Enable deep checking. Check every Zenko bucket for its backing bucket
                (same as zcheck buckets)

buckets
^^^^^^^

Check every Zenko bucket for its backend bucket.
