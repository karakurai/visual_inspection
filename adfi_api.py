import base64
import datetime
import json
import os
from io import BytesIO

import cv2
import numpy as np
import requests
from PIL import Image


class AdfiApi:
    def __init__(
        self, apikey, aimodel_id, model_type, url, ok_dir, not_clear_dir, ng_dir
    ):
        self.apikey = apikey
        self.aimodel_id = aimodel_id
        self.model_type = model_type
        if url[-1] != "/":
            self.url = url + "/"
        else:
            self.url = url
        self.height = 800
        self.width = 800
        current_day = datetime.datetime.now().strftime("%Y%m%d")
        if ok_dir[-1] != "/":
            self.ok_dir = ok_dir + "/" + current_day + "/"
        else:
            self.ok_dir = ok_dir + current_day + "/"
        if not_clear_dir[-1] != "/":
            self.not_clear_dir = not_clear_dir + "/" + current_day + "/"
        else:
            self.not_clear_dir = not_clear_dir + current_day + "/"
        if ng_dir[-1] != "/":
            self.ng_dir = ng_dir + "/" + current_day + "/"
        else:
            self.ng_dir = ng_dir + current_day + "/"

    def inspect_image(self, img_filepath, result_image=True):
        img = Image.open(img_filepath).convert("RGB")

        # Notice: Please make the image size smaller than 800 pix.
        MAX_SIZE = 800
        self.height = img.height
        self.width = img.width
        if img.height > MAX_SIZE:
            self.height = MAX_SIZE
        if img.width > MAX_SIZE:
            self.width = MAX_SIZE
        img = img.resize((self.width, self.height), Image.ANTIALIAS)
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes = img_bytes.getvalue()
        files = {"image_data": (img_filepath, img_bytes, "image/png")}
        data = {
            "apikey": self.apikey,
            "aimodel_id": self.aimodel_id,
            "model_type": self.model_type,
            "result_image": result_image,
        }

        # Send a request.
        response = requests.post(self.url, files=files, data=data)

        # if the request fails.
        if response.status_code != 200:
            return None, None

        result_json = response.json()
        result_image_save_path = None

        if result_image:
            # Convert a string to a result image
            img_binary = base64.b64decode(
                result_json["result_image_base64_data"].encode("utf-8")
            )
            img_array = np.frombuffer(img_binary, dtype=np.uint8)
            result_image_np = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            result_image_save_path = os.path.basename(img_filepath)

            if "Anomaly" in result_json["result"]:
                if not os.path.exists(self.ng_dir):
                    os.makedirs(self.ng_dir)
                result_image_save_path = self.ng_dir + result_image_save_path
            elif "Not-clear" in result_json["result"]:
                if not os.path.exists(self.not_clear_dir):
                    os.makedirs(self.not_clear_dir)
                result_image_save_path = self.not_clear_dir + result_image_save_path
            else:
                if not os.path.exists(self.ok_dir):
                    os.makedirs(self.ok_dir)
                result_image_save_path = self.ok_dir + result_image_save_path

            # Save the result image
            result_image_np = cv2.resize(result_image_np, (img.width, img.height))
            cv2.imwrite(result_image_save_path, result_image_np)

        return result_json, result_image_save_path


class AdfiLocalModelApi:
    model = None
    info_dict = None
    model_path = None

    def __init__(self, model_path, confini_settings):
        self.vit = False
        self.confini_settings = confini_settings
        self.file_extension = model_path.split(".")[-1]
        if self.file_extension == "vit_model":
            self.vit = True
            if os.path.isfile("./adfi_vit_local/adfi_vit.py"):
                self.model_path = model_path
                from adfi_vit_local import adfi_vit

                self.model = adfi_vit.AI_Model()
                self.model.load(self.model_path)
                self.info_dict = self.model.get_info()
                print("License expiration date: ", self.info_dict["expiration_date"])
        else:
            if os.path.isfile("./adfi_local/adfi.py"):
                self.model_path = model_path
                from adfi_local import adfi

                self.model = adfi.AI_Model()
                self.model.load(self.model_path)
                self.info_dict = self.model.get_info()
                print("License expiration date: ", self.info_dict["expiration_date"])
            current_day = datetime.datetime.now().strftime("%Y%m%d")
            if self.confini_settings["result_dir_ok"][-1] != "/":
                self.ok_dir = (
                    self.confini_settings["result_dir_ok"] + "/" + current_day + "/"
                )
            else:
                self.ok_dir = self.confini_settings["result_dir_ok"] + current_day + "/"
            if self.confini_settings["result_dir_not_clear"][-1] != "/":
                self.not_clear_dir = (
                    self.confini_settings["result_dir_not_clear"]
                    + "/"
                    + current_day
                    + "/"
                )
            else:
                self.not_clear_dir = (
                    self.confini_settings["result_dir_not_clear"] + current_day + "/"
                )
            if self.confini_settings["result_dir_ng"][-1] != "/":
                self.ng_dir = (
                    self.confini_settings["result_dir_ng"] + "/" + current_day + "/"
                )
            else:
                self.ng_dir = self.confini_settings["result_dir_ng"] + current_day + "/"

    def inspect_image(self, img_filepath, result_image=True):
        result_image_save_path = None

        if self.file_extension == "vit_model":
            prediction_dict = self.model.predict(img_filepath)
            result_dict = {
                "image_name": os.path.basename(img_filepath),
                "result": str(prediction_dict["category"]),
                "time": str(datetime.datetime.now()),
                "score": str(prediction_dict["score"]),
                "class": str(prediction_dict["class"]),
                "category": str(prediction_dict["category"]),
                "category_list": prediction_dict["category_list"],
                "score_list": prediction_dict["score_list"],
                "vit": self.vit,
            }
            return result_dict, result_image_save_path

        else:
            prediction_dict = self.model.predict(
                img_filepath, get_result_image=result_image
            )

            result_dict = {
                "image_name": os.path.basename(img_filepath),
                "result": str(prediction_dict["result"]),
                "time": str(datetime.datetime.now()),
                "anomaly_score": str(prediction_dict["score"]),
                "main_prediction_result": str(prediction_dict["main"]),
                "sub_prediction_result": str(prediction_dict["sub"]),
                "vit": self.vit,
            }

            if result_image:
                result_image_save_path = os.path.basename(img_filepath)

                if "Anomaly" in prediction_dict["result"]:
                    if not os.path.exists(self.ng_dir):
                        os.makedirs(self.ng_dir)
                    result_image_save_path = self.ng_dir + result_image_save_path
                elif "Not-clear" in prediction_dict["result"]:
                    if not os.path.exists(self.not_clear_dir):
                        os.makedirs(self.not_clear_dir)
                    result_image_save_path = self.not_clear_dir + result_image_save_path
                else:
                    if not os.path.exists(self.ok_dir):
                        os.makedirs(self.ok_dir)
                    result_image_save_path = self.ok_dir + result_image_save_path

                # Save the result image
                prediction_dict["result_image"].save(result_image_save_path)

            return result_dict, result_image_save_path
