"""
A visualization tool built on top of the standard cProfile and pstats modules, using pygame
"""

import sys
import os
import time
import argparse
import pygame
import squarify
from pygame.locals import *
import random

def get_random_color(pastel_factor = 0.5):
	return tuple(int(255*(x+pastel_factor)/(1.0+pastel_factor)) for x in [random.uniform(0,1.0) for i in [1,2,3]])

def color_distance(c1,c2):
	return sum([abs(x[0]-x[1]) for x in zip(c1,c2)])

def generate_new_color(existing_colors,pastel_factor = 0.5):
	max_distance = None
	best_color = None
	for i in range(0,100):
		color = get_random_color(pastel_factor = pastel_factor)
		if not existing_colors:
			return color
		best_distance = min([color_distance(color,c) for c in existing_colors])
		if not max_distance or best_distance > max_distance:
			max_distance = best_distance
			best_color = color
	return best_color

def main() -> int:
	"""
	Runs the main routine, and returns an exit code.
	"""
	if not pygame.font:
		print("Warning, fonts disabled", file=sys.stderr)

	parser = argparse.ArgumentParser(description="A visualization tool built on top of the standard cProfile and pstats modules, using pygame")
	parser.add_argument("SCRIPT", type=str, help="The path to the script you wish to profile.")

	args = parser.parse_args()

	if not os.path.isfile(args.SCRIPT):
		print("Error, no such file: '%s'" % args.SCRIPT, file=sys.stderr)
		return 1

	# This bit is pretty much exactly the way the cProfile module does it:
	progname = os.path.basename(args.SCRIPT)
	sys.path.insert(0, os.path.dirname(progname))

	with open(args.SCRIPT, 'rb') as f:
		code = compile(f.read(), progname, 'exec')

	globs = {
		'__file__': progname,
		'__name__': '__main__',
		'__package__': None,
		'__cached__': None
	}

	import cProfile

	pr = cProfile.Profile()

	print("(visualprofiler): BEGIN '%s' OUTPUT" % progname)

	pr.runctx(code, globs, None)

	print("(visualprofiler): END '%s' OUTPUT" % progname)

	stats = pr.getstats()
	stats.sort(key=lambda x: x.totaltime, reverse=True)

	pygame.init()
	displayInfo = pygame.display.Info()

	screenSize = (int(displayInfo.current_w//2), int(displayInfo.current_h//2))
	font_size = int(0.013*screenSize[1])
	white = (255, 255, 255)
	black = (0, 0, 0)
	# limeGreen = (50, 205, 50)
	# paleBlue = (145, 163, 210)
	# paleTurquoise = (175, 255, 222)

	myFont = pygame.font.SysFont("Calibri", font_size)


	normalizedSizes = squarify.normalize_sizes([stat.totaltime for stat in stats], *screenSize)
	statAreas = [((int(x['x']), int(x['y'])), (int(x['dx']), int(x['dy']))) for x in squarify.squarify(normalizedSizes, 0., 0., *screenSize)]

	print(*(stat[0][0] for stat in statAreas), sep='\n')
	print()

	screen = pygame.display.set_mode(screenSize)
	pygame.display.set_caption("Profile of '%s'" % progname)
	screen.fill(white)
	pygame.display.update()

	squares, colors = [], []
	for i, (pos, size) in enumerate(statAreas):
		if isinstance(stats[i].code, str):
			name = stats[i].code
		else:
			name = "%s on line %d in %s" % (stats[i].code.co_name, stats[i].code.co_firstlineno, stats[i].code.co_filename)
		newcolor = generate_new_color(colors)
		print(newcolor)
		colors.append(newcolor)
		newSurface = pygame.Surface(size)
		newSurface.fill(newcolor)
		newText = myFont.render(name, 1, black)
		newSurface.blit(newText, (size[0]//2 - len(str(code)), size[1]//2 - font_size))
		squares.append((name, pos, newSurface))
		screen.blit(newSurface, pos)

	pygame.display.update()

	#main loop
	while True:
		time.sleep(0.05)
		for event in pygame.event.get():

			#handle window close
			if event.type == pygame.QUIT:
				pygame.display.quit()
				pygame.quit()
				return 0
		pygame.display.update()
