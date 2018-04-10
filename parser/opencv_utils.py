from random import random

import cv2


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
