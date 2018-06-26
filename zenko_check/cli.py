import click
from collections import namedtuple
from .helm import Status as HelmStatus
from .orbit import OverlayConfig
from .print import print_sections
from . import __version__ as zenko_check_version
from .check import check_backends, check_buckets
from .bucket import UserBuckets

import sys
from pprint import pprint

ZCConf = namedtuple('ZCConf', ('mongo', 'helm_release', 'output', 'verbose'))
NO_HELM_REL = ['help', 'version']
REQ_HELM_REL = ['k8s']

# Root
@click.group()
@click.option('--mongo', default = None, type = str, help = 'Override the default mongo host:port')
@click.option('--helm-release', '-r', type = str, help ='The release name helm was installed under')
@click.option('--output', '-o', type = click.File(mode='w'))
@click.option('--verbose', '-v', is_flag=True, help="Enable verbose output, WARNING: This will print your access keys to the terminal or file!")
@click.pass_context
def zenko_check(ctx, **kwargs):
	subcmd = ctx.invoked_subcommand
	if kwargs.get('helm_release') is None:
		if subcmd in REQ_HELM_REL or (kwargs.get('mongo') is None and subcmd not in NO_HELM_REL):
			raise click.UsageError('Missing option "--helm-release" / "-r"', ctx=ctx)
	if 'output' not in kwargs:
		kwargs['output'] = None
	ctx.obj = ZCConf(**kwargs)

#help
@zenko_check.command(help = 'Access usage help for commands')
@click.argument('command', required = False)
@click.pass_context
def help(ctx, command):
	if command:
		cmd = zenko_check.get_command(ctx, command)
		if cmd:
			click.echo(cmd.get_help(ctx))
		else:
			click.secho('%s is not a valid command!'%command, fg='red')
	else:
		click.echo(zenko_check.get_help(ctx))

# version
@zenko_check.command(help='Print version')
def version():
	click.echo('zenko-check', nl = False)
	click.secho('\tv%s'%zenko_check_version, fg='green')

# k8s
@zenko_check.command(help = 'Checks related to the kubernetes cluster')
@click.pass_obj
@click.option('--check-services', '-c', is_flag = True, help = 'Attempt to connect to defined services and report their status')
def k8s(conf, check_services):
	hs = HelmStatus(conf.helm_release, check_services=check_services)
	hs.pull_status()
	print_sections(hs.repr, width=100, file=conf.output)

# orbit
@zenko_check.command(help = "Check relating to Orbit's configuration")
@click.pass_obj
def orbit(conf):
	oc = OverlayConfig(helm_release = conf.helm_release, mongo = conf.mongo, verbose=conf.verbose)
	print_sections(oc.repr, file=conf.output)

# backend
@zenko_check.command(help = 'Check backend buckets for existence and configuration')
@click.option('--deep', '-d', is_flag = True, help = 'Enable deep checking. Check every zenko bucket for its respective backend bucket')
@click.pass_context
def backends(ctx, deep):
	conf = ctx.obj
	oc = OverlayConfig(helm_release = conf.helm_release, mongo = conf.mongo, verbose=conf.verbose)
	print_sections({'backends':list(check_backends(oc))})
	if deep:
		ctx.invoke(buckets)

# Check zenko buckets
@zenko_check.command(help = 'Check every Zenko bucket for its respective backing bucket')
@click.pass_obj
def buckets(conf):
	oc = OverlayConfig(helm_release = conf.helm_release, mongo = conf.mongo, verbose=conf.verbose)
	ub = UserBuckets(helm_release=conf.helm_release, mongo = conf.mongo)
	print_sections({'buckets': list(check_buckets(oc, ub.buckets))})

# Do EVERYTHING!!
@zenko_check.command(help = 'Run all checks and tests')
@click.pass_context
def checkup(ctx):
	if not ctx.obj.helm_release:
		raise click.UsageError('Missing option "--helm-release" / "-r"', ctx=ctx)
	ctx.invoke(orbit)
	ctx.invoke(k8s, check_services = True)
	ctx.invoke(backends)
	ctx.invoke(buckets)
