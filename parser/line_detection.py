from operator import attrgetter

from parser.invoice_image import InvoiceImage
import numpy as np
import cv2

from parser.opencv_utils import swap_colors, save_image
from parser.utils import temporary_file_name


class LineCoordinates:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __repr__(self):
        return repr((self.x1, self.y1, self.x2, self.y2))


def join_horizontal_lines(horizontal_lines):
    joined_lines = [horizontal_lines[0]]
    for index, line in enumerate(horizontal_lines[1:]):
        previous_line = joined_lines.pop()
        if previous_line.y1 == line.y1:
            x_values = [previous_line.x1, previous_line.x2, line.x1, line.x2]
            previous_line.x1 = min(x_values)
            previous_line.x2 = max(x_values)
            joined_lines.append(previous_line)
        else:
            joined_lines.append(previous_line)
            joined_lines.append(line)
    return joined_lines


def join_vertical_lines(vertical_lines):
    joined_lines = [vertical_lines[0]]
    for index, line in enumerate(vertical_lines[1:]):
        previous_line = joined_lines.pop()
        if previous_line.x1 == line.x1:
            y_values = [previous_line.y1, previous_line.y2, line.y1, line.y2]
            previous_line.y1 = min(y_values)
            previous_line.y2 = max(y_values)
            joined_lines.append(previous_line)
        else:
            joined_lines.append(previous_line)
            joined_lines.append(line)
    return joined_lines


def merge_nearby_vertical_lines(vertical_lines):
    joined_lines = [vertical_lines[0]]
    for index, line in enumerate(vertical_lines[1:]):
        previous_line = joined_lines.pop()
        if abs(line.x1 - previous_line.x1) < 10:
            y_values = [previous_line.y1, previous_line.y2, line.y1, line.y2]
            x_values = [previous_line.x1, previous_line.x2, line.x1, line.x2]
            x_avg = int(sum(x_values) / len(x_values))
            joined_lines.append(LineCoordinates(x_avg, min(y_values), x_avg, max(y_values)))
        else:
            joined_lines.append(previous_line)
            joined_lines.append(line)
    return joined_lines


def merge_nearby_horizontal_lines(horizontal_lines):
    joined_lines = [horizontal_lines[0]]
    for index, line in enumerate(horizontal_lines[1:]):
        previous_line = joined_lines.pop()
        if abs(line.y1 - previous_line.y1) < 10:
            x_values = [previous_line.x1, previous_line.x2, line.x1, line.x2]
            y_values = [previous_line.y1, previous_line.y2, line.y1, line.y2]
            y_avg = int(sum(y_values) / len(y_values))
            joined_lines.append(LineCoordinates(min(x_values), y_avg, max(x_values), y_avg))
        else:
            joined_lines.append(previous_line)
            joined_lines.append(line)
    return joined_lines


def detect_vertical_lines(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_gray = cv2.GaussianBlur(gray, (5, 5), 0)
    f_p = "%s.jpg" % temporary_file_name(prefix="cropped_table")
    save_image(f_p, blur_gray)
    edges = cv2.Canny(blur_gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi, 30, minLineLength=100)
    vertical_lines = []
    if lines is None:
        return []
    for line in lines:
        for x1, y1, x2, y2 in line:
            if abs(x1 - x2) < 2 and abs(y1 - y2) > 10:
                vertical_lines.append(LineCoordinates(x1, y1, x2, y2))
    sorted_vertical_lines = sorted(vertical_lines, key=attrgetter('x1'))
    vertical_lines = join_vertical_lines(sorted_vertical_lines)
    vertical_lines = merge_nearby_vertical_lines(vertical_lines)
    # print "total line detected : %d" % len(vertical_lines)
    # for line in vertical_lines:
    #     cv2.line(invoice_image.raw_image, (line.x1, line.y1), (line.x2, line.y2), (0, 255, 0), 2)
    # cv2.imwrite("tables/lines_detected" + path + ".jpg", invoice_image.raw_image)
    return vertical_lines


def detect_horizontal_lines(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur_gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 2, 30, minLineLength=100)
    horizontal_lines = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            if abs(x1 - x2) > 10 and abs(y1 - y2) < 4:
                horizontal_lines.append(LineCoordinates(x1, y1, x2, y2))
    sorted_horizontal_lines = sorted(horizontal_lines, key=attrgetter('y1'))
    horizontal_lines = join_horizontal_lines(sorted_horizontal_lines)
    horizontal_lines = merge_nearby_horizontal_lines(horizontal_lines)
    # print "total line detected : %d" % len(horizontal_lines)
    # for line in horizontal_lines:
    #     cv2.line(invoice_image.raw_image, (line.x1, line.y1), (line.x2, line.y2), (0, 255, 0), 2)
    # cv2.imwrite("tables/lines_detected" + path + ".jpg", invoice_image.raw_image)
    return horizontal_lines
