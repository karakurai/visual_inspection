import csv
import datetime
import glob
import os
import pickle
import platform
import subprocess
import time
import webbrowser
from concurrent.futures import ThreadPoolExecutor

import cv2
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle
from kivy.graphics.texture import Texture
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen

from adfi_api import AdfiApi, AdfiLocalModelApi
from image_processing import ImageProcessing


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.api_list = []
        self.aimodel_list = []
        self.inspection_model_num = -1
        self.popup = None

    def on_enter(self):
        self.start_screen()

    def start_screen(self):
        self.app.open_inspection_cameras()
        self.ids["main_image_view"].start_clock()
        self.ids["change_button"].disabled = True
        self.ids["get_image_button"].disabled = True
        self.ids["get_image_button_0"].disabled = True
        self.ids["get_image_button_1"].disabled = True
        self.ids["get_image_button_2"].disabled = True
        self.ids["get_image_button_3"].disabled = True
        self.ids["get_image_button_4"].disabled = True
        for i in range(5):
            self.ids["preprocessing_" + str(i)].text = "-"
            self.ids["result_" + str(i)].text = ""
            self.ids["result_" + str(i)].md_bg_color = "black"
        self.ids["preprocessing_0"].text = "No AI model"
        if self.app.current_inspection_dict is not None:
            self.ids["inspection_name"].text = self.app.current_inspection_dict["NAME"]
            api_info_num = self.get_api_info()
            if (
                len(self.app.current_inspection_dict["PREPROCESSING_LIST"]) >= 1
                and api_info_num == 0
            ):
                self.ids["message"].text = self.app.textini[self.app.lang][
                    "main_message_no_api_info"
                ]
            else:
                self.ids["message"].text = self.app.textini[self.app.lang][
                    "main_message_run_inspection"
                ]
                self.ids["get_image_button"].disabled = False
                for i in range(api_info_num):
                    self.ids["preprocessing_" + str(i)].text = (
                        str(i) + ": " + self.api_list[i]["NAME"]
                    )
                    self.ids["get_image_button_" + str(i)].disabled = False
                if api_info_num > 1:
                    self.ids["change_button"].disabled = False
        else:
            self.ids["message"].text = self.app.textini[self.app.lang][
                "main_massage_no_inspection"
            ]
            self.ids["message"].text_color = "white"
            self.ids["message"].md_bg_color = "black"

    def leave_screen(self):
        self.ids["main_image_view"].stop_clock()
        self.ids["main_image_view"].clear()
        self.app.release_cameras()
        self.ids["message"].text = self.app.textini[self.app.lang][
            "main_massage_loading_camera"
        ]
        self.ids["message"].text_color = "white"
        self.ids["message"].md_bg_color = "black"
        self.ids["get_image_button"].disabled = True
        self.ids["get_image_button_0"].disabled = True
        self.ids["get_image_button_1"].disabled = True
        self.ids["get_image_button_2"].disabled = True
        self.ids["get_image_button_3"].disabled = True
        self.ids["get_image_button_4"].disabled = True
        self.ids["save_0"].disabled = True
        self.ids["save_1"].disabled = True
        self.ids["save_2"].disabled = True
        self.ids["save_3"].disabled = True
        self.ids["save_4"].disabled = True
        self.api_list = []
        self.aimodel_list = []
        for i in range(5):
            self.ids["preprocessing_" + str(i)].text = "-"
            self.ids["result_" + str(i)].text = ""
            self.ids["result_" + str(i)].md_bg_color = "black"

    def get_api_info(self):
        self.api_list = []
        self.aimodel_list = []
        if (
            self.app.current_inspection_dict is not None
            and len(self.app.current_inspection_dict["PREPROCESSING_LIST"]) >= 1
        ):
            preprocessing_list = self.app.current_inspection_dict["PREPROCESSING_LIST"]
            for i in range(len(preprocessing_list)):
                if "LOCAL" in preprocessing_list[i] and preprocessing_list[i]["LOCAL"]:
                    self.api_list.append(preprocessing_list[i])
                    adfi_api = AdfiLocalModelApi(
                        preprocessing_list[i]["MODEL_PATH"],
                        self.app.confini["settings"],
                    )
                    if (
                        adfi_api.info_dict is not None
                        and adfi_api.info_dict["available"]
                    ):
                        self.aimodel_list.append(adfi_api)
                    else:
                        if adfi_api.info_dict is not None:
                            message = self.app.textini[self.app.lang][
                                "main_toast_error_message_not_available"
                            ]
                            if self.app.lang == "ja":
                                message = (
                                    message + " " + adfi_api.info_dict["message_ja"]
                                )
                            else:
                                message = message + " " + adfi_api.info_dict["message"]
                            toast(message)
                else:
                    if (
                        "API_KEY" in preprocessing_list[i]
                        and "MODEL_ID" in preprocessing_list[i]
                        and "MODEL_TYPE" in preprocessing_list[i]
                    ):
                        if (
                            preprocessing_list[i]["API_KEY"] != ""
                            and preprocessing_list[i]["MODEL_ID"] != ""
                            and preprocessing_list[i]["MODEL_TYPE"] != ""
                        ):
                            self.api_list.append(preprocessing_list[i])
                            adfi_api = AdfiApi(
                                preprocessing_list[i]["API_KEY"],
                                preprocessing_list[i]["MODEL_ID"],
                                preprocessing_list[i]["MODEL_TYPE"],
                                self.app.confini["settings"]["adfi_api_url"],
                                self.app.confini["settings"]["result_dir_ok"],
                                self.app.confini["settings"]["result_dir_not_clear"],
                                self.app.confini["settings"]["result_dir_ng"],
                            )
                            self.aimodel_list.append(adfi_api)
        return len(self.api_list)

    def start_inspection(self):
        self.ids["get_image_button"].disabled = True
        self.ids["get_image_button_0"].disabled = True
        self.ids["get_image_button_1"].disabled = True
        self.ids["get_image_button_2"].disabled = True
        self.ids["get_image_button_3"].disabled = True
        self.ids["get_image_button_4"].disabled = True
        self.ids["message"].text = self.app.textini[self.app.lang][
            "main_message_inspection_in_progress"
        ]
        self.ids["message"].text_color = "black"
        self.ids["message"].md_bg_color = "yellow"

    def finish_inspection(self):
        self.ids["get_image_button"].disabled = False
        for i in range(len(self.aimodel_list)):
            self.ids["get_image_button_" + str(i)].disabled = False
        self.ids["message"].text = self.app.textini[self.app.lang][
            "main_message_run_inspection"
        ]
        self.ids["message"].text_color = "white"
        self.ids["message"].md_bg_color = "black"

    def show_image_popup(self, image_path, title="Image", result=None):
        if self.popup is None:
            new_popup = Popup(
                title=title,
                content=PopupImageScreen(dismiss_popup=self.dismiss_popup),
                size_hint=(0.9, 0.9),
            )
            new_popup.content.set_image_path(image_path)
            new_popup.title = title
            new_popup.content.ids["result"].opacity = 1
            if result == "Anomaly":
                new_popup.content.ids["result"].text = self.app.textini[self.app.lang][
                    "main_result_ng"
                ]
                new_popup.content.ids["result"].md_bg_color = "red"
            elif result == "Not-clear":
                new_popup.content.ids["result"].text = self.app.textini[self.app.lang][
                    "main_result_not_clear"
                ]
                new_popup.content.ids["result"].md_bg_color = "gray"
            else:
                new_popup.content.ids["result"].opacity = 0
            self.popup = new_popup
            self.app.popup_is_open = True
            self.popup.open()

    def show_save_image_popup(self, image_path, index):
        if self.popup is None:
            title = "Save Image " + str(index) + ":" + self.api_list[int(index)]["NAME"]
            new_popup = Popup(
                title=title,
                content=PopupSaveImageScreen(dismiss_popup=self.dismiss_popup),
                size_hint=(0.9, 0.9),
            )
            new_popup.content.set_image_path_and_name(
                image_path, self.api_list[int(index)]["NAME"]
            )
            new_popup.title = title
            self.popup = new_popup
            self.app.popup_is_open = True
            self.popup.open()

    def dismiss_popup(self):
        self.popup.dismiss()
        self.popup = None
        self.app.popup_is_open = False


class MainImageView(MDFloatLayout):
    def __init__(self, **kwargs):
        super(MainImageView, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.image_processing = ImageProcessing()
        self.screen = None
        self.pos = (300, 270)
        self.image_size = (
            int(self.app.confini["settings"]["image_max_width"]),
            int(self.app.confini["settings"]["image_max_height"]),
        )
        self.full_frame = [None] * 5
        self.frame = [None] * 5
        self.frame_list = [None] * 5
        self.frame_list_max = 5
        self.current_image_num = 0
        self.tmp_texture = None
        self.current_inspection_dir = "./adfi_client_app_data/current_inspection"
        self.image_dict = {}
        self.get_image_flg = False
        self.processing = -1
        self.inspection_image_path_list = [None] * 5
        self.result_image_path_list = [None] * 5

    def clear(self):
        self.full_frame = [None] * 5
        self.frame = [None] * 5
        self.frame_list = [None] * 5
        self.frame_list_max = 5
        self.current_image_num = 0
        self.tmp_texture = None
        self.image_dict = {}
        self.canvas.before.clear()
        self.inspection_image_path_list = [None] * 5
        self.result_image_path_list = [None] * 5

    def change_image(self):
        if self.screen is None:
            self.screen = self.app.sm.get_screen("main")
        if len(self.screen.api_list) > 0:
            settings_list = self.screen.api_list
            self.current_image_num += 1
            if len(settings_list) <= self.current_image_num:
                self.current_image_num = 0
            self.screen.ids["image_name"].text = settings_list[self.current_image_num][
                "NAME"
            ]

    def start_clock(self):
        Clock.schedule_interval(
            self.clock_capture, 1.0 / float(self.app.confini["settings"]["display_fps"])
        )

    def stop_clock(self):
        Clock.unschedule(self.clock_capture)

    def clock_capture(self, dt):
        if self.screen is None:
            self.screen = self.app.sm.get_screen("main")

        if len(self.screen.api_list) > 0:
            settings_list = self.screen.api_list
            for i in range(5):
                tmp_cap = self.app.camera_list[i]
                if tmp_cap is not None:
                    ret, tmp_frame = tmp_cap.read()
                    if not ret:
                        return
                    if tmp_frame is not None:
                        tmp_list = self.frame_list[i]
                        if tmp_list is None:
                            tmp_list = [tmp_frame]
                        else:
                            tmp_list.append(tmp_frame)
                        self.frame_list[i] = tmp_list
                        if len(self.frame_list[i]) > self.frame_list_max:
                            del self.frame_list[i][0]

                if self.frame_list[i] is not None:
                    self.full_frame[i] = self.image_processing.multi_frame_smoothing(
                        self.frame_list[i]
                    )
                    self.frame[i] = self.app.resize_cv_image(
                        self.app.crop_image_ratio(
                            self.full_frame[i],
                            self.app.current_ratio1[i],
                            self.app.current_ratio2[i],
                        ),
                        size_max=self.image_size,
                    )

            for i in range(len(settings_list)):
                setting = settings_list[i]
                if self.frame[setting["CAMERA_NUM"]] is not None:
                    crop_bg = None
                    filepath = (
                        self.current_inspection_dir
                        + "/"
                        + self.app.current_inspection_dict["FILENAME"]
                        + "_"
                        + setting["FILENAME"]
                        + ".png"
                    )
                    if setting["BG_IMAGE"] and os.path.exists(filepath):
                        crop_bg = self.app.resize_cv_image(
                            self.app.crop_image_ratio(
                                cv2.imread(filepath),
                                self.app.current_ratio1[setting["CAMERA_NUM"]],
                                self.app.current_ratio2[setting["CAMERA_NUM"]],
                            ),
                            size_max=self.image_size,
                        )
                    tmp_frame = self.image_processing.do_image_processing(
                        self.frame[setting["CAMERA_NUM"]],
                        setting,
                        bg_image=crop_bg,
                    )
                    self.image_dict.update(
                        {
                            str(i): tmp_frame,
                        }
                    )
                    if i == self.current_image_num:
                        tmp_frame = self.app.resize_cv_image(tmp_frame)
                        flip_frame = cv2.flip(tmp_frame, 0)
                        if flip_frame is not None:
                            buf = flip_frame.tobytes()
                            texture = Texture.create(
                                size=(tmp_frame.shape[1], tmp_frame.shape[0]),
                                colorfmt="bgr",
                            )
                            texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
                            self.tmp_texture = texture

            if self.tmp_texture is not None:
                if self.processing == -1:
                    self.canvas.before.clear()
                    self.canvas.before.add(Color(rgb=[1, 1, 1]))
                    self.canvas.before.add(
                        Rectangle(
                            texture=self.tmp_texture,
                            pos=self.pos,
                            size=self.tmp_texture.size,
                        )
                    )
                elif self.processing == 0:
                    self.processing = -1
                    self.screen.finish_inspection()

                # inspection
                if self.get_image_flg:
                    self.get_image_flg = False
                    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    current_day = datetime.datetime.now().strftime("%Y%m%d")
                    data_dir = (
                        self.app.confini["settings"]["inspection_image_dir"]
                        + "/"
                        + str(current_day)
                    )
                    if not os.path.exists(data_dir):
                        os.makedirs(data_dir)
                    save_image_path = [""] * len(settings_list)
                    if any(self.image_dict):
                        img_count = 0
                        for i, value in self.image_dict.items():
                            index = int(i)
                            save_image_name = (
                                self.app.current_inspection_dict["NAME"]
                                + "_"
                                + settings_list[index]["NAME"]
                                + "_"
                                + settings_list[index]["FILENAME"]
                            )
                            save_image_path[index] = (
                                data_dir
                                + "/"
                                + str(current_time)
                                + "_"
                                + save_image_name
                                + ".png"
                            )
                            img_count += 1
                        self.processing = 0
                        with ThreadPoolExecutor(max_workers=img_count) as executor:
                            for j in range(len(settings_list)):
                                if (
                                    self.inspection_model_num == -1
                                    or self.inspection_model_num == j
                                ):
                                    if save_image_path[j] != "":
                                        self.screen.ids[
                                            "result_" + str(j)
                                        ].md_bg_color = "yellow"
                                        executor.submit(
                                            self.do_inspection(
                                                j,
                                                save_image_path[j],
                                                self.screen.ids["save_results"].active,
                                                self.screen.ids["save_image"].active,
                                            )
                                        )

    def get_images(self, model_num):
        self.inspection_model_num = model_num
        self.get_image_flg = True
        if self.screen is None:
            self.screen = self.app.sm.get_screen("main")
        for i in range(5):
            self.screen.ids["result_" + str(i)].text = ""
            self.screen.ids["result_" + str(i)].md_bg_color = "black"
        self.screen.start_inspection()

    def do_inspection(
        self,
        index,
        save_image_path,
        result_image_flg,
        save_image_flg,
    ):
        time.sleep(index * 0.1)
        if not os.path.exists(self.app.confini["settings"]["result_csv_dir"]):
            os.makedirs(self.app.confini["settings"]["result_csv_dir"])
        result_csv_path = (
            self.app.confini["settings"]["result_csv_dir"]
            + "/"
            + datetime.datetime.now().strftime("%Y%m")
            + "_result.csv"
        )
        result_vit_csv_path = (
            self.app.confini["settings"]["result_csv_dir"]
            + "/"
            + datetime.datetime.now().strftime("%Y%m")
            + "_vit_result.csv"
        )

        self.processing += 1
        cv2.imwrite(
            save_image_path,
            self.image_dict[str(index)],
        )
        if len(self.screen.aimodel_list) > index:
            result_json, result_image_save_path = self.screen.aimodel_list[
                index
            ].inspect_image(save_image_path, result_image_flg)
            if result_json is None:
                toast(
                    self.screen.api_list[index]["NAME"]
                    + ": "
                    + self.app.textini[self.app.lang]["main_toast_error_api"]
                )
                self.screen.ids["result_" + str(index)].text = self.app.textini[
                    self.app.lang
                ]["main_result_error"]
                self.screen.ids["result_" + str(index)].md_bg_color = "black"
            else:
                if result_json["vit"]:
                    self.screen.ids["result_" + str(index)].text = result_json["result"]
                    self.screen.ids["result_" + str(index)].md_bg_color = "green"
                else:
                    if "Anomaly" in result_json["result"]:
                        self.screen.ids["result_" + str(index)].text = self.app.textini[
                            self.app.lang
                        ]["main_result_ng"]
                        self.screen.ids["result_" + str(index)].md_bg_color = "red"
                        if result_image_save_path is not None:
                            self.show_result_image(
                                str(index), result_image_save_path, "Anomaly"
                            )
                    elif "Not-clear" in result_json["result"]:
                        self.screen.ids["result_" + str(index)].text = self.app.textini[
                            self.app.lang
                        ]["main_result_not_clear"]
                        self.screen.ids["result_" + str(index)].md_bg_color = "gray"
                        if result_image_save_path is not None:
                            self.show_result_image(
                                str(index), result_image_save_path, "Not-clear"
                            )
                    else:
                        self.screen.ids["result_" + str(index)].text = self.app.textini[
                            self.app.lang
                        ]["main_result_ok"]
                        self.screen.ids["result_" + str(index)].md_bg_color = "green"

            if not save_image_flg:
                os.remove(save_image_path)
                self.inspection_image_path_list[int(index)] = None
                self.screen.ids["text_save_train_image"].opacity = 0
                self.screen.ids["save_" + str(index)].opacity = 0
                self.screen.ids["save_" + str(index)].disabled = True
            else:
                self.inspection_image_path_list[int(index)] = save_image_path
                self.screen.ids["text_save_train_image"].opacity = 1
                self.screen.ids["save_" + str(index)].opacity = 1
                self.screen.ids["save_" + str(index)].disabled = False
                if result_json is not None:
                    if result_json["vit"]:
                        if not os.path.exists(result_vit_csv_path):
                            row = ["image_name", "result", "time", "score", "class"]
                            for cotegory in result_json["category_list"]:
                                row.append(cotegory)

                            with open(result_vit_csv_path, "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerow(row)
                        row_list = [
                            result_json["image_name"],
                            result_json["result"],
                            result_json["time"],
                            result_json["score"],
                            result_json["class"],
                        ]
                        for score in result_json["score_list"]:
                            row_list.append(score)
                        with open(result_vit_csv_path, "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow(row_list)
                    else:
                        if not os.path.exists(result_csv_path):
                            with open(result_csv_path, "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerow(
                                    [
                                        "image_name",
                                        "result",
                                        "time",
                                        "anomaly_score",
                                        "main_prediction_result",
                                        "sub_prediction_result",
                                    ]
                                )
                        with open(result_csv_path, "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow(
                                [
                                    result_json["image_name"],
                                    result_json["result"],
                                    result_json["time"],
                                    result_json["anomaly_score"],
                                    result_json["main_prediction_result"],
                                    result_json["sub_prediction_result"],
                                ]
                            )
            self.result_image_path_list[int(index)] = result_image_save_path
        self.processing -= 1

    def show_image(self, result_num):
        inspection_img_path = self.inspection_image_path_list[int(result_num)]
        if inspection_img_path is not None and os.path.exists(inspection_img_path):
            open_image(inspection_img_path)
        result_img_path = self.result_image_path_list[int(result_num)]
        if result_img_path is not None and os.path.exists(result_img_path):
            self.show_result_image(result_num, result_img_path)

    def show_result_image(self, result_num, result_img_path, result=None):
        if result_img_path is not None and os.path.exists(result_img_path):
            self.screen.show_image_popup(
                result_img_path, title="Result Image " + str(result_num), result=result
            )

    def show_save_image(self, result_num):
        inspection_img_path = self.inspection_image_path_list[int(result_num)]
        if inspection_img_path is not None and os.path.exists(inspection_img_path):
            self.screen.show_save_image_popup(
                inspection_img_path,
                result_num,
            )


class PopupImageScreen(MDBoxLayout):
    dismiss_popup = ObjectProperty(None)

    def set_image_path(self, value):
        if os.path.exists(value):
            self.ids.popup_image.source = value
        else:
            print(f"Image path does not exist: {value}")


class PopupSaveImageScreen(MDBoxLayout):
    dismiss_popup = ObjectProperty(None)
    original_image = None
    aimodel_name = None

    def __init__(self, **kwargs):
        super(PopupSaveImageScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def set_image_path_and_name(self, value, name):
        if os.path.exists(value):
            self.ids.popup_save_image.source = value
            self.original_image = cv2.imread(value)
            self.aimodel_name = name
            self.ids.popup_save_dir_path.text = os.path.abspath(
                self.app.confini["settings"]["dataset_dir"]
            )
        else:
            print(f"Image path does not exist: {value}")

    def save_image(self, class_label=0):
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M_%S")
        if self.original_image is not None and self.aimodel_name is not None:
            dataset_dir = self.app.confini["settings"]["dataset_dir"]
            if not os.path.exists(dataset_dir):
                os.makedirs(dataset_dir)
            filename = str(current_time) + ".png"
            if class_label == 0:
                save_dataset_dir = (
                    dataset_dir + "/Inspection_" + self.aimodel_name + "_Normal"
                )
                filename = "Normal_" + filename
            else:
                save_dataset_dir = (
                    dataset_dir + "/Inspection_" + self.aimodel_name + "_Anomaly"
                )
                filename = "Anomaly_" + filename
            if not os.path.exists(save_dataset_dir):
                os.makedirs(save_dataset_dir)
            save_image_path = save_dataset_dir + "/" + filename
            cv2.imwrite(
                save_image_path,
                self.original_image,
            )
            toast(self.app.textini[self.app.lang]["main_toast_save_image"])
        self.dismiss_popup()


def open_image(image_path):
    try:
        image_path = os.path.abspath(image_path)
        if not os.path.exists(image_path):
            print(f"Image path does not exist: {image_path}")
            return
        system = platform.system()
        if system == "Windows":
            os.startfile(image_path)
        elif system == "Darwin":
            subprocess.call(["open", image_path])
        else:
            subprocess.call(["xdg-open", image_path])
    except Exception as e:
        print(str(e))
