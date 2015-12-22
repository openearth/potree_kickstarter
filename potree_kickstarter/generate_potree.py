"""generate_potree

	Usage:
		generate_potree.py generate-potree <lat> <lon> <output>
		generate_potree.py (-h | --help)

	Arguments:
		<lat> latitude of your location
		<lon> longitude of your location
		<output> output location of the potree octree

	Options:
		-h --help	Show this screen

"""

from docopt import docopt
#import ahn2potree as ap 

if __name__ == '__main__':
	args = docopt(__doc__)

	import ahn2potree as ap
	import os

	kaart = ap.coordinates2bladnr(float(args['<lat>']), float(args['<lon>']))
	lasfile = ap.get_lasfiles(kaart)
	x_max, x_min, y_max, y_min = ap.get_boundingbox(lasfile)
	img = ap.get_aerialphoto(x_max, x_min, y_max, y_min, 8000, 8000, kaart)
	las_c = ap.merge_lasfiles(kaart)
	color_lasfile = ap.merge_color(img, las_c, kaart)
	ap.create_potree(color_lasfile, os.path.abspath(os.path.join(os.path.dirname(__file__), args['<output>'])), kaart)

