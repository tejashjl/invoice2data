"""
Keep helper functions not related to specific module.
"""
import os
import tempfile
import io
import yaml
from collections import OrderedDict
import subprocess

from wand.color import Color
from wand.image import Image as wi
from PIL import Image
# from parser.opencv_utils import check_image_contains_text

RESOLUTION = 500  # resolution must be a (x, y) pair or an integer of the same x/y


# borrowed from http://stackoverflow.com/a/21912744
def ordered_load(
        stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict
):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)

    return yaml.load(stream, OrderedLoader)


def temporary_file_name(prefix="invoice_"):
    """ returns a temporary file-name """
    temporary_file = tempfile.NamedTemporaryFile(prefix=prefix)
    return temporary_file.name


def cleanup(filename):
    """ tries to remove the given filename. Ignores non-existent files """
    try:
        os.remove(filename)
    except OSError:
        pass


def empty_dir(folder):
    print os.getcwd()
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def convert_pdf_to_images(pdf_file_path):
    image_file_paths = []
    with wi(filename=pdf_file_path, resolution=RESOLUTION) as img:
        # img.compression_quality = 99
        with img.convert('jpg') as pdfImages:
            for pdfImage in pdfImages.sequence:
                image = wi(image=pdfImage)
                image.format = 'jpeg'
                file_name = '{}{}.jpg'.format(temporary_file_name(), len(image_file_paths))
                image.save(filename=file_name)
                tiff_file_name = '{}{}.tiff'.format(temporary_file_name(), len(image_file_paths))
                convert = "convert -units PixelsPerInch %s -density 300 %s" % (file_name, tiff_file_name)
                subprocess.Popen(convert.split(' '), stdout=subprocess.PIPE).communicate()
                image_file_paths.append(tiff_file_name)
    return image_file_paths
