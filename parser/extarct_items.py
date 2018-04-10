from operator import attrgetter
from tesserocr import PyTessBaseAPI, RIL
from flask import json
from parser.invoice_image import InvoiceImage
from parser.line_detector import detect_lines, detect_horizontal_lines
from parser.line_item import LineItem
import logging as logger
from parser.opencv_utils import save_image, swap_colors, crop, convert_color, convert_to_black_and_white
from parser.utils import empty_dir, cleanup, temporary_file_name

api = PyTessBaseAPI()


class IndexRegion:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y

    def __repr__(self):
        return repr((self.text, self.x, self.y))


def get_table_x_pos(width):
    aspect_ratio = 80.0 / 1239.0
    return int(aspect_ratio * width)


def get_table_y_pos(height, page_number):
    if page_number == 1:
        aspect_ratio = 1000.0 / 1754.0
    else:
        aspect_ratio = 380.0 / 1754.0
    return int(aspect_ratio * height)


def get_index_y_pos(width):
    aspect_ratio = 60.0 / 1239.0
    return int(aspect_ratio * width)


def crop_table(invoice_img):
    height, width, mode = invoice_img.raw_image.shape
    cropped = crop(invoice_img.raw_image, get_table_x_pos(width), get_table_y_pos(height, invoice_img.page_number),
                   width, height)
    return cropped


def crop_table_index(invoice_table):
    height, width, mode = invoice_table.shape
    cropped = crop(invoice_table, 0, 0, get_index_y_pos(width), height)
    return cropped


def get_box_key_value(box, key, padding):
    return box[key] + padding if box[key] + padding != 0 else box[key]


def extract_index_regions(table_index_region):
    table_index_region_file_path = '%s.jpg' % temporary_file_name(prefix="tess")
    save_image(table_index_region_file_path, table_index_region)
    extracted_index_regions = []
    api.SetVariable("classify_bln_numeric_mode", "1")
    api.SetImageFile(table_index_region_file_path)
    api.SetPageSegMode(4)
    ocrResult = api.GetUTF8Text()
    raw_text_array = ocrResult.splitlines()
    text_array = filter(lambda x: len(x) > 0, raw_text_array)
    boxes = api.GetComponentImages(RIL.TEXTLINE, True)
    for i, (im, box, _, _) in enumerate(boxes):
        if text_array[i].strip().isdigit():
            extracted_index_regions.append(IndexRegion(text_array[i].strip(), box['x'], box['y']))
    cleanup(table_index_region_file_path)
    return extracted_index_regions


def sort_regions_by_y_axis(index_regions):
    return sorted(index_regions, key=attrgetter('y'))


def crop_line_items(invoice_table, extracted_index_regions):
    cropped_line_items = []
    height, width, mode = invoice_table.shape
    for index, index_region in enumerate(extracted_index_regions):

        if index != len(extracted_index_regions) - 1:
            next_region = extracted_index_regions[index + 1]
        else:
            next_region = IndexRegion("", index_region.x, height)
        line_item = crop(invoice_table, index_region.x - 5, index_region.y - 10, width, next_region.y)
        cropped_line_items.append(line_item)
        # save_image('line-items' + str(index) + '.jpg', line_item)
    return cropped_line_items


def get_line_items_regions(invoice_image):
    invoice_table = crop_table(invoice_image)
    table_index_region = crop_table_index(invoice_table)
    extracted_index_regions = extract_index_regions(table_index_region)
    sorted_index_regions = sort_regions_by_y_axis(extracted_index_regions)
    cropped_line_items = crop_line_items(invoice_table, sorted_index_regions)
    return cropped_line_items


def extract_text(region):
    file_path = '%s.jpg' % temporary_file_name(prefix="tess")
    save_image(file_path, region)
    api.SetVariable("classify_bln_numeric_mode", "0")
    api.SetImageFile(file_path)
    api.SetPageSegMode(4)
    ocrResult = api.GetUTF8Text()
    cleanup(file_path)
    return ocrResult.strip()


def crop_line_regions(line_item_region, vertical_lines):
    cropped_regions = []
    width, height, _ = line_item_region.shape
    for index, line in enumerate(vertical_lines):
        x = vertical_lines[index - 1].x1 if index > 0 else 0
        region = crop(line_item_region, x, 0, line.x1, height)
        cropped_regions.append(region)
    return cropped_regions


def extract_line_items(invoice_image):
    line_items = []
    line_items_regions = get_line_items_regions(invoice_image)
    logger.debug("Number of line items: %d", len(line_items_regions))
    for line_item_region in line_items_regions:
        vertical_lines = detect_lines(line_item_region)
        cropped_regions = crop_line_regions(line_item_region, vertical_lines)
        lineItem = LineItem()
        for index, cropped_region in enumerate(cropped_regions):
            text = extract_text(cropped_region)
            if index == 0:
                lineItem.set_description(text)
            if index == 1:
                lineItem.set_catalog(text)
            if index == 2:
                lineItem.set_amount(text)
            if index == 3:
                lineItem.set_price_per_unit(text)
            if index == 4:
                lineItem.set_discount(text)
            if index == 5:
                lineItem.set_net_amount(text)
            if index == 6:
                lineItem.set_ust(text)
        logger.debug(json.dumps(lineItem.__dict__))
        line_items.append(lineItem.__dict__)
    return line_items


def get_footer_height(height):
    aspect_ratio = 120.0 / 1754.0
    return int(aspect_ratio * height)


def crop_footer(invoice_image):
    height, width, mode = invoice_image.raw_image.shape
    cropped_invoice = crop(invoice_image.raw_image, 0, 0, width, height - get_footer_height(height))
    return cropped_invoice


def crop_details_table(invoice):
    height, width, _ = invoice.shape
    horizontal_lines = detect_horizontal_lines(invoice)
    cropped_invoice = crop(invoice, 0, 0, width, horizontal_lines[len(horizontal_lines) - 2].y1)
    return cropped_invoice


def extract_items(image_file_path, page_number=0, last_page=False):
    invoice_image = InvoiceImage(image_file_path, page_number)
    # TODO: Check if footer is present
    if True:
        cropped_invoice = crop_footer(invoice_image)
    # TODO: Check if details table present in last page
    if last_page and True:
        cropped_invoice = crop_details_table(cropped_invoice)
    invoice_image.raw_image = cropped_invoice
    line_items = extract_line_items(invoice_image)
    return line_items
