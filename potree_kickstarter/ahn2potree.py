"""

"""

# # Import packages
import logging
import json
import os
import urlparse
import subprocess

#logging.root.setLevel(logging.DEBUG)

# computing
import numpy as np

# plotting
import matplotlib.pyplot as plt

# # for spatial types
import owslib.wfs
import owslib.wms
# # for spatial operations
import shapely.geometry

# # for pointclouds
import liblas
from liblas import file

# for downloading
# import requests
# # for xml parsing
import lxml.etree

# for aerial photo saturation
import skimage as ski
# import gdal

# for coordinate transformation
import osgeo.osr

# for wms template
from mako.template import Template

# for adjusting image saturation
# from skimage import color

# define wgs84 to rd converter
wgs84 = osgeo.osr.SpatialReference()
wgs84.ImportFromEPSG(4326)
rd = osgeo.osr.SpatialReference()
rd.ImportFromEPSG(28992)
wgs842rd = osgeo.osr.CoordinateTransformation(wgs84, rd)


# input
# define target location coordinates
lat, lon = 51.57, 3.57

# TODO: write function to check if external dependencies work

# function checks in which 'bladnummer' the input location is located en returns the name of the 'bladnummer'
def coordinates2bladnr(lat, lon):
    wfsurl = 'http://geodata.nationaalgeoregister.nl/ahn2/wfs'
    wfs = owslib.wfs.WebFeatureService(wfsurl, version="2.0.0")
    wfslayer = wfs.contents['ahn2:ahn2_bladindex']

    # Get boxes from WFS
    f = wfs.getfeature(typename=[wfslayer.id], outputFormat="json")
    data = json.load(f)  # Coordinate system, 5 coordinates of polygon, bladnr

    shapes = []
    tiles = []

    # create a list of tiles and shapes
    for feature in data['features']:
        shapes.append(shapely.geometry.asShape(feature['geometry'])[0])
        tiles.append(shapes[-1].exterior.coords[:])

    x, y, _ = wgs842rd.TransformPoint(lon, lat)
    p = shapely.geometry.Point(x, y)

    # Check in which box the point lies
    for i, shape in enumerate(shapes):
        if p.within(shape):
            bladnr = data['features'][i]['properties']['bladnr']
            logging.info('The point is in box %s.', bladnr)
            break
    return bladnr


# download the pointclouds for a given bladnummer
def get_lasfiles(bladnr):
    urls = [
        'http://geodata.nationaalgeoregister.nl/ahn2/atom/ahn2_uitgefilterd.xml',
        'http://geodata.nationaalgeoregister.nl/ahn2/atom/ahn2_gefilterd.xml'
    ]
    for url in urls:
        tree = lxml.etree.parse(url)
        links = tree.findall('//{http://www.w3.org/2005/Atom}link')
        links = [link.attrib['href'] for link in links if bladnr in link.attrib['href']]
        link = links[0]
        filename = os.path.split(urlparse.urlsplit(link).path)[-1]
        newname = filename.replace('.zip', '')

        # skip if the extracted file is already there
        if os.path.exists(newname):
            logging.info('%s is alreadt available, %s will not be downloaded', newname, link)
            lasfile = newname
        elif os.path.exists('c' + bladnr + '.laz'):
            logging.info('%s is alreadt available, %s will not be downloaded', 'c' + bladnr + '.laz', link)
            lasfile = 'c' + bladnr + '.laz'
        elif os.path.exists(bladnr + '_color.laz'):
            logging.info('%s is alreadt available, %s will not be downloaded', bladnr + '_color.laz', link)
            lasfile = bladnr + '_color.laz'
        else:
            # continue downloading
            wget = subprocess.call(["wget", "-c", link])
            unzip = subprocess.call(["unzip", "-o", filename])
            os.remove(filename)
            lasfile = filename
    return lasfile

# functions returns bounding box of the lasfile
def get_boundingbox(lasfile):
    # read header of lasfiles to receive bounding box
    f = file.File(lasfile, mode='r')
    max = f.header.get_max()
    min = f.header.get_min()
    x_max = max[0]
    x_min = min[0]
    y_max = max[1]
    y_min = min[1]
    f.close()
    if x_max is None:
        logging.info('Unable to read bounding box')
    return x_max, x_min, y_max, y_min


# Get geotiff of a given bounding box from nationaal georegister
def get_aerialphoto(x_max, x_min, y_max, y_min, size_x, size_y, bladnr):
    image = bladnr + '.tiff'
    output_name = bladnr + '_saturated.tiff'
    if os.path.exists(output_name):
        logging.info('%s is already available. Image will not be downloaded and processed', output_name)
    else:
        # create wms request from wms template
        wms_template = Template(filename='wms_template.xml')  # load xml template

        # fill in variables
        a = wms_template.render(x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, x_size=size_x, y_size=size_y)

        f = open('wms.xml', 'w')
        f.write(a)  # write xml to file for wms request
        f.close()

        # download image
        if os.path.exists(image):
            logging.info('image already available, %s will not be downloaded', image)
        else:
            subprocess.call(["gdal_translate", "wms.xml", output_name])

        # img = (plt.imread(image)).astype(np.uint8)

        # # split image in N steps for processing (otherwise to much for virtual memory)
        # img_new = np.zeros_like(img).astype(np.float)  # new empty array to fill with saturated rgb

        # pic_size = float(len(img))           # no. of pixels in 1 direction
        # n = 4                                # no. of processing steps
        # steps = pic_size / n                 # pixels per processing step

        # for i in range(n):
        #     lower = i * int(steps)
        #     upper = (i + 1) * int(steps)

        #     img_process = img[lower:upper, :, :]
        #     hsv = ski.color.rgb2hsv(img_process)
        #     hsv[:, :, 1] *= 1.5
        #     img_new[lower:upper, :, :] = ski.color.hsv2rgb(hsv)

        #     # clear memory for next step
        #     img_process = None
        #     hsv = None

        # plt.imsave(output_name, arr=img_new, format='tiff')  # save picture as tiff (spatial information lost)

        # img_new = None
        # img = None

        # # spatial information is lost in saturated tiff. Copy spatial info from original tiff
        # # get geo information from tiff file with spatial information
        # ds_input = gdal.Open(image)
        # projection = ds_input.GetProjection()
        # geotransform = ds_input.GetGeoTransform()
        # gcp_count = ds_input.GetGCPs()

        # ds_output = gdal.Open(output_name, gdal.GA_Update)  # saturated tiff file without spatial information

        # ds_output.SetProjection(projection)  # copy spatial info
        # ds_output.SetGeoTransform(geotransform)
        # ds_output.SetGCPs(gcp_count, ds_input.GetGCPProjection())

        # # close dataset
        # ds_input = None
        # ds_output = None

        # os.remove(image)  # remove nonstaturated geotiff
    return output_name


# merge the "uitgefilterd" and "gefilterd" lasfiles.
def merge_lasfiles(bladnr):
    las_u = 'u' + bladnr + '.laz'
    las_g = 'g' + bladnr + '.laz'
    las_c = 'c' + bladnr + '.laz'
    if os.path.exists(las_c):
        logging.info('%s is already available, lasfiles are not merged ', las_c)
    elif os.path.exists(bladnr + '_color.laz'):
        logging.info('%s is already available, lasfiles are not merged ', bladnr + '_color.laz')
    else:
        tmp = subprocess.call(["lasmerge","-i", las_g, "-i", las_u, "-o", las_c])
        os.remove('u' + bladnr + '.laz')
        os.remove('g' + bladnr + '.laz')
        if tmp == 0:
            logging.info("succesfully merged")
        else:
            logging.info("something went wrong in merging")
        
    return las_c

# merge the aerial photo and lasfile to a lasfile with color.
def merge_color(img,las_c, bladnr):
    output = bladnr + '_color.laz'
    if os.path.exists(output):
        logging.info('%s is already available, color merge will not be executed', output)
    else:
        tmp = subprocess.call(["las2las", "--color-source", img, "--point-format", "3", "--color-source-bands", "1", "2", "3",
                         "--color-source-scale", "256", "-i", las_c, "-o", output])
        os.remove(las_c)
        if tmp == 0:
            logging.info("color merge was succesfull")
        else:
            logging.info("something went wrong in color merge")
    return output


# create potree octree with website from.
def create_potree(lasfile, outputdirectory, bladnr):
    tmp = subprocess.call(["PotreeConverter", lasfile, "-l", "9", "--generate-page", bladnr, "-o", outputdirectory])
    if tmp == 0:
        logging.info("succesfill generated potree octree")
    else:
        logging.info("something went wrong in PotreeConverter")


if __name__ == "__main__":
    kaart = coordinates2bladnr(lat, lon)
    lasfile = get_lasfiles(kaart)
    x_max, x_min, y_max, y_min = get_boundingbox(lasfile)
    img = get_aerialphoto(x_max, x_min, y_max, y_min, 8000, 8000, kaart)
    las_c = merge_lasfiles(kaart)
    color_lasfile = merge_color(img, las_c, kaart)
    create_potree(color_lasfile, os.path.abspath(os.path.join(os.path.dirname(__file__), 'potree')), kaart)
