from operator import attrgetter
from random import random
from tesserocr import PyTessBaseAPI

import cv2

from parser.index_region import IndexRegion
from parser.utils import temporary_file_name, cleanup


def save_image(file_name, img_mat):
    cv2.imwrite(file_name, img_mat)


def crop(image, x, y, x1, y1):
    return image[y:y1, x:x1]


def swap_colors(img_mat):
    rows, cols = img_mat.shape
    for i in range(rows):
        for j in range(cols):
            img_mat[i, j] = 0 if img_mat[i, j] == 255 else 255
    # save_image("swapped" + str(random()) + ".jpg", img_mat)
    return img_mat


def convert_color(image, code):
    return cv2.cvtColor(image, code)


def convert_to_black_and_white(image):
    (thresh, im_bw) = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # save_image('bw_image' + str(random()) + '.png', im_bw)
    return im_bw


def sort_regions_by_y_axis(regions):
    return sorted(regions, key=attrgetter('y'))


def crop_regions(image, regions):
    cropped_regions = []
    height, width, mode = image.shape
    for index, index_region in enumerate(regions):
        if index != len(regions) - 1:
            next_region = regions[index + 1]
        else:
            next_region = IndexRegion("", index_region.x, height)
        line_item = crop(image, index_region.x - 5, index_region.y - 10, width, next_region.y)
        cropped_regions.append(line_item)
    return cropped_regions


def crop_line_regions(line_item_region, vertical_lines):
    cropped_regions = []
    width, height, _ = line_item_region.shape
    for index, line in enumerate(vertical_lines):
        x = vertical_lines[index - 1].x1 if index > 0 else 0
        region = crop(line_item_region, x, 0, line.x1, height)
        cropped_regions.append(region)
    return cropped_regions


def extract_text(region):
    api = PyTessBaseAPI()
    file_path = '%s.jpg' % temporary_file_name(prefix="tess")
    save_image(file_path, region)
    api.SetVariable("classify_bln_numeric_mode", "0")
    api.SetImageFile(file_path)
    api.SetPageSegMode(4)
    ocrResult = api.GetUTF8Text()
    cleanup(file_path)
    return ocrResult.strip()
