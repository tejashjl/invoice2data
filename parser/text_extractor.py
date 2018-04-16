import pyocr
import sys
import logging as logger

from PIL import Image

tools = pyocr.get_available_tools()
if len(tools) == 0:
    logger.error("No OCR tool found")
    sys.exit(1)
tool = tools[0]
logger.debug("Using OCR tool '%s'" % (tool.get_name()))


def get_word_boxes_from_image(image_path):
    word_boxes = tool.image_to_string(
        Image.open(image_path),
        lang="eng+deu",
        builder=pyocr.builders.WordBoxBuilder()
    )
    return word_boxes