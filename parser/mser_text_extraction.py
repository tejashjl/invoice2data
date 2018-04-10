import cv2
import imutils
import numpy as np

from parser.utils import temporary_file_name


class MserFeature:
    mser = cv2.MSER_create()
    debug = True

    def __init__(self):
        pass

    def detect_regions(self, invoice_image):
        original_image = invoice_image.image
        preprocessed_image = self.preprocessed_image(invoice_image=invoice_image.image)
        regions, _ = self.mser.detectRegions(preprocessed_image)
        hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in regions]
        cv2.polylines(original_image, hulls, 1, (0, 255, 0))
        if self.debug:
            output_file_path = '%s.jpg' % temporary_file_name(prefix="mser_")
            cv2.imwrite(output_file_path, original_image)

    def preprocessed_image(self, invoice_image):
        rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))
        sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        gray_image = cv2.cvtColor(invoice_image, cv2.COLOR_BGR2GRAY)
        # thresh_binary = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        tophat = cv2.morphologyEx(gray_image, cv2.MORPH_TOPHAT, rectKernel)
        cv2.imshow("Show", tophat)
        cv2.waitKey()
        cv2.destroyAllWindows()
        gradX = cv2.Sobel(tophat, ddepth=cv2.CV_32F, dx=1, dy=0,
                          ksize=-1)
        gradX = np.absolute(gradX)
        (minVal, maxVal) = (np.min(gradX), np.max(gradX))
        gradX = (255 * ((gradX - minVal) / (maxVal - minVal)))
        gradX = gradX.astype("uint8")

        gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)
        thresh = cv2.threshold(gradX, 0, 255,
                               cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # apply a second closing operation to the binary image, again
        # to help close gaps between credit card number regions
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)

        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        locs = []
        for (i, c) in enumerate(cnts):
            (x, y, w, h) = cv2.boundingRect(c)
            ar = w / float(h)
            cv2.rectangle(invoice_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        locs = sorted(locs, key=lambda x: x[0])
        output = []
        cv2.imshow("Show", invoice_image)
        cv2.waitKey()
        cv2.destroyAllWindows()
        return invoice_image
