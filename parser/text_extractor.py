import pyocr
import sys
import logging as logger

from PIL import Image

from parser.text_corrector import HunSpell

tools = pyocr.get_available_tools()
if len(tools) == 0:
    logger.error("No OCR tool found")
    sys.exit(1)
tool = tools[0]
logger.debug("Using OCR tool '%s'" % (tool.get_name()))
hunspell = HunSpell()

def extract_text_regions(image_path):

    word_boxes = tool.image_to_string(
        Image.open(image_path),
        lang="eng+deu",
        builder=pyocr.builders.WordBoxBuilder()
    )
    return word_boxes


def extract_plain_text(image_path):
    txt = tool.image_to_string(
        Image.open(image_path),
        lang="eng+deu",
        builder=pyocr.builders.TextBuilder()
    )
    return txt
