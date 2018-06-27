import click
from math import floor
from .util import mark_last
from io import StringIO
import termcolor

MAX_GAP = 10

def color_text(text):
	if isinstance(text, tuple):
		return termcolor.colored(*text)
	return text

def strip_color(line):
	if isinstance(line, tuple):
		return line[0]
	return line

def find_col_max_widths(section, numcols):
	max_per_col = []
	for col in range(numcols):
		longest = max([len(strip_color(l[col])) for l in section])
		max_per_col.append(longest)
	return max_per_col

def distribute_extra(widths, numcols, extra):
	per_col = floor(extra / numcols)
	widths = list(map(lambda x: x + per_col, widths))
	leftover = extra - (per_col * numcols)
	if leftover:
		min_len = min(widths)
		pos = widths.index(min_len)
		widths[pos] += leftover
	return widths

def find_col_widths(section,  numcols, width = 80):
	if numcols == 1:
		return [width]
	max_per_col = find_col_max_widths(section, numcols)
	naive_per_col = floor(width / numcols)
	widths = []
	for i in range(numcols):
		if max_per_col[i] > naive_per_col:
			widths.append(max_per_col[i])
		else:
			if naive_per_col - max_per_col[i] >= MAX_GAP:
				widths.append(max_per_col[i])
			else:
				widths.append(naive_per_col)
	return widths










def print_line(l, spaced = False, file = None, **kwargs):
	if spaced:
		click.secho('\n ' + l + '\n', **kwargs)
	else:
		click.secho(' '+ l, **kwargs)

def print_padded(line, width, pad = ' ', **kwargs):
	pad_width = int((width - len(line)) / 2)
	padding = pad * pad_width
	print_line('%s%s%s'%(padding, line, padding), **kwargs)

def print_header(s, width = 80, pad = '=', fg = 'cyan', level = 0, **kwargs):
	inner_width = width - (5 * level)
	inner = '{:{fill}^{width}}'.format(' %s '%s, width = inner_width, fill = pad)
	line = '{:^{width}}'.format(inner, width=width)
	print_line(line, fg = fg, spaced = True, **kwargs)

def print_colored_row(row, widths = None, total_width = None, **kwargs):
	if not widths:
		widths = [0] * len(row)
	if total_width:
		if len(row) == 1:
			extra_padding = int((total_width - sum(widths)) / 2)
		else:
			extra_padding = int((total_width - sum(widths)) / (len(row) - 1))
		if extra_padding < 0:
			extra_padding = 0
	else:
		extra_padding = 0
	for i, col in enumerate(row):
		if isinstance(col, tuple):
			line, color = col
		else:
			line = col
			color = None
		# print(i, len(row)-1, end='')
		if i == len(row) - 1:
			nl = True
		else:
			nl = False
		if i < len(row) - 1 or len(row) == 1:
			if len(row) == 1:
				print_line(left_pad(line, widths[i] + extra_padding), fg = color, nl = nl, **kwargs)
			elif widths:
				print_line(right_pad(line, widths[i] + extra_padding), fg = color, nl = nl, **kwargs)
			else:
				print_line(right_pad(line, extra_padding + 1), fg = color, nl = nl, **kwargs)
		else:
			print_line(line, fg = color, nl = nl, **kwargs)

def print_row(row, total_width = 80, **kwargs):
	cols = len(row)
	col_width = floor(total_width / cols)
	colored_row = [color_text(c)[:col_width] for c in row]
	tmpl = '{:<{width}}'
	# click.echo
	# click.echo(tmpl.format(*colored_row, width=col_width))
	for last, col in mark_last(colored_row):
		print_line(tmpl.format(col, width=col_width), nl=last, **kwargs)







def max_length(lines, col):
	m = 0
	for line in lines:
		if len(strip_color(line[col])) > m:
			m = len(strip_color(line[col]))
	return m

def left_pad(line, width, pad = ' '):
	return '%s%s'%(pad*(width - len(line)), line)

def right_pad(line, width, pad = ' '):
	return '%s%s'%(line, pad * (width - len(line)))

def print_columns(cols, **kwargs):
	for row in cols:
		print_row(row, **kwargs)

def print_sections(sections, width = 80, _level = 0, **kwargs):
	for heading, section in sections.items():
		print_header(heading.upper(), **kwargs, level = _level, width = width)
		if isinstance(section, dict):
			print_sections(section, width = width, _level = _level + 1, **kwargs)
		else:
			print_columns(section, total_width = width - 5, **kwargs)
