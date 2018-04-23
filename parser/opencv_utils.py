from operator import attrgetter

import cv2

from parser.index_region import IndexRegion
from parser.text_extractor import extract_plain_text
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
    return img_mat


def convert_color(image, code):
    return cv2.cvtColor(image, code)


def convert_to_black_and_white(image):
    (thresh, im_bw) = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
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
    file_path = '%s.jpg' % temporary_file_name(prefix="tess")
    save_image(file_path, region)
    text = extract_plain_text(file_path)
    cleanup(file_path)
    return text.strip()


def remove_images_without_text(file_paths):
    text_image_file_paths = []
    for file_path in file_paths:
        text_regions = detect_contours(file_path)
        if len(text_regions) > 100:
            text_image_file_paths.append(file_path)
        else:
            cleanup(file_path)
    return text_image_file_paths


def detect_contours(file_path):
    image = cv2.imread(file_path)
    imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 127, 255, 0)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours
