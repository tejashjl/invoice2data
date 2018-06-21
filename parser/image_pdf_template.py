from collections import OrderedDict

from flask import json
import cv2
import numpy as np

from parser.field_value_extractor import extract_field_values
from parser.index_region import IndexRegion
from parser.invoice_image import InvoiceImage
from parser.line_detection import detect_horizontal_lines, detect_vertical_lines
from parser.opencv_utils import crop, save_image, sort_regions_by_y_axis, crop_regions, \
    crop_line_regions, extract_text, remove_images_without_text, detect_mser_regions
from parser.text_extractor import extract_text_regions
from parser.utils import ordered_load, convert_pdf_to_images, cleanup, temporary_file_name
import logging as logger


class BBoxes:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


def assert_content(tpl):
    required_fields = ['width', 'height', 'line_items_table', 'line_items_index', 'summary_table', 'footer']
    for field in required_fields:
        assert field in tpl.keys(), 'Missing %s field.' % field
    if 'line_items_table' in tpl.keys():
        assert 'fields' in tpl['line_items_table'], 'Missing fields field.'
        assert 'first_page' in tpl['line_items_table'], 'Missing first_page field.'
        assert 'remaining_pages' in tpl['line_items_table'], 'Missing remaining_pages field.'
    if 'line_items_index' in tpl.keys():
        assert 'present' in tpl['line_items_index'], 'Missing present field.'
        if tpl['line_items_index']['present']:
            assert 'ending_x_pos' in tpl['line_items_index'], 'Missing ending_x_pos field.'
    if 'summary_table' in tpl.keys():
        assert 'present' in tpl['summary_table'], 'Missing present field.'
    if 'footer' in tpl.keys():
        assert 'present' in tpl['footer'], 'Missing present field.'
        if tpl['footer']['present']:
            assert 'height' in tpl['footer'], 'Missing present field.'


def get_template(template):
    tpl = ordered_load(template.read())
    assert_content(tpl)
    return InvoiceTemplate(tpl)


class InvoiceTemplate(OrderedDict):
    def __init__(self, *args, **kwargs):
        super(InvoiceTemplate, self).__init__(*args, **kwargs)

    def extract_data(self, path):
        output = {}
        image_file_paths = convert_pdf_to_images(path)
        image_file_paths = remove_images_without_text(image_file_paths)
        logger.debug('Number of PDF pages: %d', len(image_file_paths))
        for index, image_file in enumerate(image_file_paths):
            logger.debug('Parsing page: (%d/%d)', index, len(image_file_paths))
            is_last_page = (len(image_file_paths) == (index + 1))
            output['page-' + str(index)] = self.parse_image(image_file_path=image_file, page_number=index + 1,
                                                       last_page=is_last_page)
        # [cleanup(file_path) for file_path in image_file_paths]
        return output

    def parse_image(self, image_file_path, page_number, last_page):
        parsed_data = {}
        invoice_image = InvoiceImage(image_file_path, page_number)
        if 'fields' in self.keys():
            field_values = extract_field_values(image_file_path, self['fields'])
            parsed_data['fields'] = field_values
        if self['footer']['present']:
            cropped_invoice = self.crop_footer(invoice_image)
        else:
            cropped_invoice = invoice_image.raw_image
        if last_page and self['summary_table']['present']:
            cropped_invoice = self.crop_summary_table(cropped_invoice)
        line_items = self.extract_line_items(original_image=invoice_image, cropped_image=cropped_invoice)
        parsed_data['line_items'] = line_items
        return parsed_data


    def crop_footer(self, invoice_image):
        height, width, mode = invoice_image.raw_image.shape
        cropped_invoice = crop(invoice_image.raw_image, 0, 0, width, height - self.get_footer_height(height))
        return cropped_invoice

    def get_footer_height(self, height):
        aspect_ratio = self['footer']['height'] / self['height']
        return int(aspect_ratio * height)

    def crop_summary_table(self, invoice):
        height, width, _ = invoice.shape
        horizontal_lines = detect_horizontal_lines(invoice.copy())
        cropped_invoice = crop(invoice, 0, 0, width, horizontal_lines[len(horizontal_lines) - 2].y1)
        return cropped_invoice

    def extract_line_items(self, original_image, cropped_image):
        line_items = []
        line_items_regions = self.get_line_items_regions(original_image=original_image, cropped_image=cropped_image)
        logger.debug("Number of line items: %d", len(line_items_regions))
        for line_item_region in line_items_regions:
            vertical_lines = detect_vertical_lines(line_item_region.copy())
            cropped_regions = crop_line_regions(line_item_region, vertical_lines)
            lineItem = {}
            for index, cropped_region in enumerate(cropped_regions):
                text = extract_text(cropped_region)
                if index <= len(self['line_items_table']['fields']) - 1:
                    lineItem[self['line_items_table']['fields'][index]] = text
            logger.debug(json.dumps(lineItem))
            line_items.append(lineItem)
        return line_items

    def get_line_items_regions(self, original_image, cropped_image):
        invoice_table = self.crop_table_region(original_image, cropped_image)
        table_index_region = self.crop_index_region(invoice_table)
        extracted_index_positions = self.extract_line_items_index_positions(table_index_region)
        sorted_index_positions = sort_regions_by_y_axis(extracted_index_positions)
        cropped_line_items = crop_regions(invoice_table, sorted_index_positions)
        return cropped_line_items

    def crop_table_region(self, original_image, cropped_image):
        height, width, mode = original_image.raw_image.shape
        cropped = crop(cropped_image, self.get_table_x_pos(width),
                       self.get_table_y_pos(height, original_image.page_number),
                       width, height)
        temp_file_path = "%s.jpg" % temporary_file_name(prefix="cropped_table")
        save_image(temp_file_path, cropped)
        return cropped

    def get_table_x_pos(self, width):
        aspect_ratio = self['line_items_table']['first_page']['x'] / self['width']
        return int(aspect_ratio * width)

    def get_table_y_pos(self, height, page_number):
        if page_number == 1:
            aspect_ratio = self['line_items_table']['first_page']['y'] / self['height']
        else:
            aspect_ratio = self['line_items_table']['remaining_pages']['y'] / self['height']
        return int(aspect_ratio * height)

    def crop_index_region(self, invoice_table):
        height, width, mode = invoice_table.shape
        cropped = crop(invoice_table, 0, 0, self.get_index_x_pos(width), height)
        return cropped

    def get_index_x_pos(self, width):
        aspect_ratio = self['line_items_index']['ending_x_pos'] / self['width']
        return int(aspect_ratio * width)

    def extract_line_items_index_positions(self, table_index_region):
        table_index_region_file_path = '%s.jpg' % temporary_file_name(prefix="tess")
        save_image(table_index_region_file_path, table_index_region)
        text_regions = extract_text_regions(table_index_region_file_path)
        extracted_index_regions = []
        for text_region in text_regions:
            if text_region.content.strip().isdigit():
                x = text_region.position[0][0]
                y = text_region.position[0][1]
                extracted_index_regions.append(IndexRegion(text_region.content.strip(), x, y))
        cleanup(table_index_region_file_path)
        return extracted_index_regions
