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
