import datetime
import glob
import os
import pickle
import webbrowser

import cv2
from image_processing import ImageProcessing
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle
from kivy.graphics.texture import Texture
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen


class MakingDatasetScreen(MDScreen):
    def __init__(self, **kwargs):
        super(MakingDatasetScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self):
        self.app.open_inspection_cameras()

    def on_enter(self):
        self.ids["dataset_image_view"].start_clock()
        if self.app.current_inspection_dict is None:
            self.ids["change_button"].disabled = True
            self.ids["normal_button"].disabled = True
            self.ids["anomaly_button"].disabled = True
            self.ids["message"].text = (
                self.app.textini[self.app.lang]["making_dataset"]
                + " :  "
                + self.app.textini[self.app.lang]["md_error_message"]
            )
        else:
            self.ids["change_button"].disabled = False
            self.ids["normal_button"].disabled = False
            self.ids["anomaly_button"].disabled = False
            self.ids["message"].text = (
                self.app.textini[self.app.lang]["making_dataset"]
                + "  "
                + self.app.textini[self.app.lang]["md_message"]
            )
            if len(self.app.current_inspection_dict["PREPROCESSING_LIST"]) <= 1:
                self.ids["change_button"].disabled = True

            self.ids["image_name"].text = self.app.current_inspection_dict[
                "PREPROCESSING_LIST"
            ][0]["NAME"]
            self.ids["inspection_name"].text = str(
                self.app.current_inspection_dict["NAME"]
            )
        self.ids["save_dir_path"].text = os.path.abspath(
            self.app.confini["settings"]["dataset_dir"]
        )

        self.ids["normal_num"].text = str(
            self.ids["dataset_image_view"].get_image_count(0)
        )
        self.ids["anomaly_num"].text = str(
            self.ids["dataset_image_view"].get_image_count(1)
        )

    def open_ADFI(self):
        url = "https://adfi.jp/"
        if self.app.lang == "ja":
            url = "https://adfi.jp/ja/"
        webbrowser.open(url, new=1, autoraise=True)


class DatasetImageView(MDFloatLayout):
    def __init__(self, **kwargs):
        super(DatasetImageView, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.image_processing = ImageProcessing()
        self.screen = None
        self.pos = (200, 200)
        self.image_size = (500, 500)
        self.full_frame = [None] * 5
        self.frame = [None] * 5
        self.frame_list = [None] * 5
        self.frame_list_max = 5
        self.current_image_num = 0
        self.tmp_texture = None
        self.current_inspection_dir = "./adfi_client_app_data/current_inspection"
        self.image_dict = {}

    def clear(self):
        self.full_frame = [None] * 5
        self.frame = [None] * 5
        self.frame_list = [None] * 5
        self.frame_list_max = 5
        self.current_image_num = 0
        self.tmp_texture = None
        self.image_dict = {}

    def change_image(self):
        if self.screen is None:
            self.screen = self.app.sm.get_screen("making_dataset")
        self.current_image_num += 1
        if (
            len(self.app.current_inspection_dict["PREPROCESSING_LIST"])
            <= self.current_image_num
        ):
            self.current_image_num = 0
        self.screen.ids["image_name"].text = self.app.current_inspection_dict[
            "PREPROCESSING_LIST"
        ][self.current_image_num]["NAME"]

    def start_clock(self):
        Clock.schedule_interval(self.clock_capture, 1.0 / float(self.app.confini["settings"]["display_fps"]))

    def stop_clock(self):
        Clock.unschedule(self.clock_capture)

    def clock_capture(self, dt):
        if self.app.current_inspection_dict is not None:
            settings_list = self.app.current_inspection_dict["PREPROCESSING_LIST"]
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

            count = 0
            for setting in settings_list:
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
                            setting["NAME"] + "_" + setting["FILENAME"]: tmp_frame,
                        }
                    )
                    if count == self.current_image_num:
                        flip_frame = cv2.flip(tmp_frame, 0)
                        if flip_frame is not None:
                            buf = flip_frame.tobytes()
                            texture = Texture.create(
                                size=(tmp_frame.shape[1], tmp_frame.shape[0]),
                                colorfmt="bgr",
                            )
                            texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
                            self.tmp_texture = texture
                    count += 1

            if self.tmp_texture is not None:
                self.canvas.before.clear()
                self.canvas.before.add(Color(rgb=[1, 1, 1]))
                self.canvas.before.add(
                    Rectangle(
                        texture=self.tmp_texture,
                        pos=self.pos,
                        size=self.tmp_texture.size,
                    )
                )

    def get_image_count(self, class_label=0):
        image_count = 0
        if self.app.current_inspection_dict is not None:
            settings = self.app.current_inspection_dict["PREPROCESSING_LIST"]
            if len(settings) > 0:
                key = settings[0]["NAME"] + "_" + settings[0]["FILENAME"]
                if class_label == 0:
                    save_dataset_dir = (
                        self.app.confini["settings"]["dataset_dir"]
                        + "/"
                        + self.app.current_inspection_dict["NAME"]
                        + "_Normal_"
                        + key
                    )
                else:
                    save_dataset_dir = (
                        self.app.confini["settings"]["dataset_dir"]
                        + "/"
                        + self.app.current_inspection_dict["NAME"]
                        + "_Anomaly_"
                        + key
                    )
                if os.path.exists(save_dataset_dir):
                    path_list = glob.glob(save_dataset_dir + "/*.png")
                    image_count = len(path_list)
        return image_count

    def save_images(self, class_label=0):
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        if self.app.current_inspection_dict is not None:
            dataset_dir = self.app.confini["settings"]["dataset_dir"]
            if not os.path.exists(dataset_dir):
                os.makedirs(dataset_dir)
            if any(self.image_dict):
                for key, value in self.image_dict.items():
                    if class_label == 0:
                        save_dataset_dir = (
                            dataset_dir
                            + "/"
                            + self.app.current_inspection_dict["NAME"]
                            + "_Normal_"
                            + key
                        )
                    else:
                        save_dataset_dir = (
                            dataset_dir
                            + "/"
                            + self.app.current_inspection_dict["NAME"]
                            + "_Anomaly_"
                            + key
                        )
                    if not os.path.exists(save_dataset_dir):
                        os.makedirs(save_dataset_dir)
                    save_image_path = (
                        save_dataset_dir + "/" + str(current_time) + ".png"
                    )
                    cv2.imwrite(
                        save_image_path,
                        value,
                    )
                toast(self.app.textini[self.app.lang]["md_toast_save_image"])
            if self.screen is None:
                self.screen = self.app.sm.get_screen("making_dataset")
            if class_label == 0:
                self.screen.ids["normal_num"].text = str(
                    self.get_image_count(class_label)
                )
            else:
                self.screen.ids["anomaly_num"].text = str(
                    self.get_image_count(class_label)
                )
