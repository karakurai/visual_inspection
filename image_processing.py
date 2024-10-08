import configparser

import cv2
import numpy as np

conf_ini = configparser.ConfigParser()
conf_ini.read("./conf.ini", encoding="utf-8")


class ImageProcessing:
    def do_image_processing(self, img, processing_list, bg_image=None):

        if "GRAY" in processing_list and processing_list["GRAY"]:
            img = self.gray(img)
            if bg_image is not None:
                bg_image = self.gray(bg_image)

        if "BLUR_METHOD" in processing_list:
            if "BLUR_KSIZE" in processing_list:
                img = self.blur(
                    img,
                    method=processing_list["BLUR_METHOD"],
                    kernel_size=processing_list["BLUR_KSIZE"],
                )
                if bg_image is not None:
                    bg_image = self.blur(
                        bg_image,
                        method=processing_list["BLUR_METHOD"],
                        kernel_size=processing_list["BLUR_KSIZE"],
                    )

            else:
                img = self.blur(img, method=processing_list["BLUR_METHOD"])
                if bg_image is not None:
                    bg_image = self.blur(
                        bg_image, method=processing_list["BLUR_METHOD"]
                    )

        if "BG_SUBTRACTION" in processing_list and processing_list["BG_SUBTRACTION"]:
            if (
                "BG_SUBTRACTION_TH" in processing_list
                and processing_list["BG_SUBTRACTION_TH"]
            ):
                if (
                    "BG_SUBTRACTION_MASK" in processing_list
                    and processing_list["BG_SUBTRACTION_MASK"]
                ):
                    img = self.background_subtraction(
                        img,
                        bg_image,
                        threshold=processing_list["BG_SUBTRACTION_TH"],
                        mask=processing_list["BG_SUBTRACTION_MASK"],
                    )
                else:
                    img = self.background_subtraction(
                        img, bg_image, threshold=processing_list["BG_SUBTRACTION_TH"]
                    )
            else:
                img = self.background_subtraction(img, bg_image)

        if "INVERT" in processing_list and processing_list["INVERT"]:
            img = self.invert(img)

        if "WHITENING" in processing_list and processing_list["WHITENING"] != 255:
            img = self.whitening(img, threshold=processing_list["WHITENING"])

        if "BLACKING" in processing_list and processing_list["BLACKING"] != 1:
            img = self.blacking(img, threshold=processing_list["BLACKING"])

        if "EDGE_METHOD" in processing_list:
            if "EDGE_KSIZE" in processing_list:
                img = self.edge(
                    img,
                    method=processing_list["EDGE_METHOD"],
                    kernel_size=processing_list["EDGE_KSIZE"],
                )
            else:
                img = self.edge(img, method=processing_list["EDGE_METHOD"])

        if "BINARIZATION" in processing_list and processing_list["BINARIZATION"]:
            if "BINARIZATION_TH" in processing_list:
                img = self.binarization(
                    img, threshold=processing_list["BINARIZATION_TH"]
                )
            else:
                img = self.binarization(img)

            if (
                "REAL_TIME_DIFF" in processing_list
                and processing_list["REAL_TIME_DIFF"]
            ):
                if "REAL_TIME_DIFF_KSIZE" in processing_list:
                    img = self.real_time_diff(
                        img, kernel_size=processing_list["REAL_TIME_DIFF_KSIZE"]
                    )
                else:
                    img = self.real_time_diff(img)

        img = self.gray_3ch(img)
        return img

    def gray(self, img):
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    def gray_3ch(self, img):
        if len(img.shape) != 3:
            img = np.stack((img,) * 3, -1)
        return img

    def blur(self, img, method="GAUSSIAN", kernel_size=5):
        if method == "GAUSSIAN":
            img = cv2.GaussianBlur(img, (kernel_size, kernel_size), sigmaX=1)
        elif method == "MEDIAN":
            img = cv2.medianBlur(img, ksize=kernel_size)
        return img

    def edge(self, img, method="LAPLACIAN", kernel_size=5):
        if method == "LAPLACIAN":
            img = cv2.Laplacian(img, -1, ksize=kernel_size)
        return img

    def binarization(self, img, threshold=127):
        if len(img.shape) == 3:
            img = self.gray(img)
        img[img < threshold] = 0
        img[img >= threshold] = 255
        return img

    def real_time_diff(self, input_img, kernel_size=5, iteration=1):
        img = input_img
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        img = cv2.dilate(img, kernel, iterations=iteration)
        img = cv2.erode(img, kernel, iterations=iteration)
        img = cv2.absdiff(input_img, img)
        return img

    def invert(self, img):
        return cv2.bitwise_not(img)

    def whitening(self, img, threshold=255):
        if threshold < 255:
            if len(img.shape) == 3:
                mask_img = self.gray(img)
                mask_img[mask_img >= threshold] = 255
                mask_img[mask_img < threshold] = 0
                mask_img = self.gray_3ch(mask_img)
                img = np.maximum(img, mask_img)
            else:
                img[img >= threshold] = 255
        return img

    def blacking(self, img, threshold=1):
        if threshold > 1:
            if len(img.shape) == 3:
                mask_img = self.gray(img)
                mask_img[mask_img < threshold] = 0
                mask_img[mask_img >= threshold] = 255
                mask_img = self.gray_3ch(mask_img)
                img = np.minimum(img, mask_img)
            else:
                img[img < threshold] = 0
        return img

    def background_subtraction(
        self, imput_img, background_img, threshold=None, mask=False
    ):
        img = imput_img
        if background_img is not None:
            if not mask:
                if len(imput_img.shape) != 3:
                    background_img = self.gray(background_img)
                if imput_img.shape == background_img.shape:
                    img = cv2.absdiff(imput_img, background_img)
                    if threshold is not None and threshold > 0:
                        np.place(img, img < threshold, 0)
            else:
                input_gray = self.gray(imput_img)
                bg_gray = self.gray(background_img)
                mask_img = cv2.absdiff(
                    self.blur(input_gray, kernel_size=7),
                    self.blur(bg_gray, kernel_size=7),
                )
                if threshold is not None and threshold > 0:
                    np.place(mask_img, mask_img < threshold, 0)
                    np.place(mask_img, mask_img >= threshold, 255)
                    if len(imput_img.shape) == 3:
                        mask_img = self.gray_3ch(mask_img)
                    img = cv2.bitwise_and(imput_img, mask_img)
        return img

    def multi_frame_smoothing(
        self, img_list, flg=conf_ini["settings"]["multi_frame_smoothing_flg"]
    ):
        list_len = len(img_list)
        img = None
        if flg != "True" or list_len == 1:
            img = img_list[-1]
        elif list_len > 1:
            img = np.zeros(img_list[0].shape, dtype="float16")
            for tmp_img in img_list:
                img = img + tmp_img / list_len
            img = img.astype("uint8")
            np.place(img, img > 255, 255)
            np.place(img, img < 0, 0)
        return img
