from operator import attrgetter

import numpy as np
import cv2

from parser.opencv_utils import save_image
from parser.utils import temporary_file_name, cleanup


class LineCoordinates:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __repr__(self):
        return repr((self.x1, self.y1, self.x2, self.y2))


def sort_line_by_x1_axis(vertical_lines):
    return sorted(vertical_lines, key=attrgetter('x1'))


def sort_line_by_y1_axis(vertical_lines):
    return sorted(vertical_lines, key=attrgetter('y1'))


def remove_nearby_vertical_lines(lines, width):
    processed_lines = []
    for index, line in enumerate(lines):
        if index != 0:
            previous_processed_line = processed_lines[len(processed_lines) - 1]
            if line.x1 - previous_processed_line.x1 < (width / 100):
                continue
        processed_lines.append(line)
    return processed_lines


def remove_nearby_horizontal_lines(lines):
    processed_lines = []
    for index, line in enumerate(lines):
        if index != 0:
            previous_processed_line = processed_lines[len(processed_lines) - 1]
            if line.y1 - previous_processed_line.y1 < 10:
                continue
        processed_lines.append(line)
    return processed_lines


def detect_vertical_lines(img):
    height, width, _ = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur_gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi, 15, np.array([]), 50, 20)
    vertical_lines = []
    for index, line in enumerate(lines):
        for x1, y1, x2, y2 in line:
            if (abs(y2 - y1)) > (height * 0.5):
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                vertical_lines.append(LineCoordinates(x1, y1, x2, y2))
    file_path = '%s.jpg' % temporary_file_name(prefix="line_detected_")
    save_image(file_path, img)
    sorted_vertical_lines = sort_line_by_x1_axis(vertical_lines)
    vertical_line = remove_nearby_vertical_lines(sorted_vertical_lines, width)
    cleanup(file_path)
    return vertical_line


def detect_horizontal_lines(img):
    height, width, _ = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur_gray, 50, 150)
    edges_file_path = '%s.jpg' % temporary_file_name(prefix="edges")
    save_image(edges_file_path, edges)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 2, 700, np.array([]), 1, 1)
    horizontal_lines = []
    line_image = np.copy(img) * 255
    for index, line in enumerate(lines):
        for x1, y1, x2, y2 in line:
            # if (abs(x2 - x1)) > (width * 0.75):1995
            if True:
                horizontal_lines.append(LineCoordinates(x1, y1, x2, y2))
                cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 1)
    lines_edges = cv2.addWeighted(img, 0.8, line_image, 1, 0)
    lines_edges_file_path = '%s.jpg' % temporary_file_name(prefix="horizontal_lines_edges")
    save_image(lines_edges_file_path, lines_edges)
    lines_file_path = '%s.jpg' % temporary_file_name(prefix="horizontal_lines_")
    save_image(lines_file_path, line_image)
    sorted_horizontal_lines = sort_line_by_y1_axis(horizontal_lines)
    horizontal_lines = remove_nearby_horizontal_lines(sorted_horizontal_lines)
    cleanup(edges_file_path)
    cleanup(lines_edges_file_path)
    cleanup(lines_file_path)
    return horizontal_lines
