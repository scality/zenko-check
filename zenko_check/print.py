import os
from .format import strip_color, color_text, find_col_widths
from functools import partial
import click
from .util import mark_last
import re
from math import ceil
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


TERM_WIDTH, TERM_HEIGHT = os.get_terminal_size()
TERM_WIDTH = min(TERM_WIDTH, 120)

control_chars = dict.fromkeys(range(32))

def pad(s, width, pad = ' ', align = 'left'):
	needed = pad * (width - len(ansi_escape.sub('', s)))
	if align == 'left':
		return s + needed
	elif align == 'right':
		return needed + s
	half = needed[:ceil(len(needed) / 2)]
	return half + s

def print_line(row, widths, ellipsize = False, align = 'left', **kwargs):
	colored = [color_text(c) for c in row]
	align = align if len(widths) > 1 else 'center'
	for last, col in mark_last(enumerate(colored)):
		i, text = col
		if not last or len(widths) == 1:
			click.echo(pad(text, widths[i], align = align) + '  ', nl = last, **kwargs)
		else:
			click.echo(text, nl = last, **kwargs)
	# click.echo(tmpl.format(*colored), **kwargs)

def print_header(s, pad = '=', fg = 'cyan', **kwargs):
	line = '{0:{fill}^{width}}'.format(' %s '%s.upper(), fill = pad, width=TERM_WIDTH)
	click.secho('\n' + line + '\n', fg = fg, **kwargs)

def print_section(section, **kwargs):
	numcols = len(section[0])
	widths = find_col_widths(section, numcols, TERM_WIDTH)
	# tmpl = ' '.join(['{:<%s}'%w for w in widths])
	align = 'center' if numcols == 1 else 'left'
	for row in section:
		print_line(row, widths, align = align)
	# map(render, section)

def print_sections(sections, **kwargs):
	for heading, section in sections.items():
		print_header(heading)
		print_section(section)
