import configparser
import glob
import os
import pickle

import cv2
from kivy.core.text import DEFAULT_FONT, LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

from aimodel_setting_screen import AimodelSettingScreen
from camera_setting_screen import CameraSettingScreen
from inspection_setting_screen import InspectionSettingScreen
from main_screen import MainScreen
from making_dataset_screen import MakingDatasetScreen
from preprocessing_screen import PreprocessingScreen
from target_area_screen import TargetAreaScreen

Window.left = 0
Window.top = 30
Window.size = (1600, 900)

WINDOWS_FONT_PATH_1 = "C:/Windows/Fonts/meiryo.ttc"
WINDOWS_FONT_PATH_2 = "C:/Windows/Fonts/YuGothM.ttc"
FONT_PATH = "./adfi_client_app_data/fonts/BIZUDPGothic-Regular.ttf"
try:
    if os.path.exists(WINDOWS_FONT_PATH_1):
        LabelBase.register(DEFAULT_FONT, WINDOWS_FONT_PATH_1)
    elif os.path.exists(WINDOWS_FONT_PATH_2):
        LabelBase.register(DEFAULT_FONT, WINDOWS_FONT_PATH_2)
    elif os.path.exists(FONT_PATH):
        LabelBase.register(DEFAULT_FONT, FONT_PATH)
except Exception as e:
    print(str(e))
Builder.load_file("./main.kv")
Builder.load_file("./camera_setting_screen.kv")
Builder.load_file("./target_area_screen.kv")
Builder.load_file("./preprocessing_screen.kv")
Builder.load_file("./inspection_setting_screen.kv")
Builder.load_file("./making_dataset_screen.kv")
Builder.load_file("./aimodel_setting_screen.kv")
Builder.load_file("./main_screen.kv")


class Tabs(TabbedPanel):
    def switch(self, tab_id):
        self.switch_to(self.ids[tab_id], do_scroll=True)


class LoadingScreen(MDScreen):
    def __init__(self, **kwargs):
        super(LoadingScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_enter(self):
        self.app.sm.add_widget(StartScreen(name="start"))
        self.app.sm.current = "start"


class StartScreen(MDScreen):
    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_enter(self):
        self.app.get_cameras()
        self.app.set_resolution_and_fps()


class QuitPopupMenu(MDBoxLayout):
    popup_close = ObjectProperty(None)


class InspectionApp(MDApp):
    camera_parameter_list = [None] * 5
    camera_list = [None] * 5
    selected_camera = None
    camera_num = None
    camera_load_flg = False
    camera_count = 0
    current_ratio1 = [[0.0, 1.0]] * 5
    current_ratio2 = [[0.0, 1.0]] * 5
    current_inspection_dict = None
    icon = "adfi_client_app_data/logo/logo.png"
    popup_is_open = BooleanProperty(False)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        self.textini = configparser.ConfigParser()
        self.textini.read("./text.ini", encoding="utf-8")
        self.confini = configparser.ConfigParser()
        self.confini.read("./conf.ini", encoding="utf-8")
        self.camera_param_dir = "./adfi_client_app_data/camera_param"
        self.lang = "DEFAULT"
        self.sm = MDScreenManager()
        self.sm.add_widget(LoadingScreen(name="loading"))
        self.tp = Tabs()
        self.title = (
            self.textini[self.lang]["adfi_app_name"]
            + " (ver. "
            + self.textini[self.lang]["version"]
            + ")"
        )
        Window.bind(on_request_close=self.popup_open)
        Window.bind(on_key_down=self.on_key_down)
        return self.sm

    def on_key_down(self, window, keycode, scancode, codepoint, modifier):
        return_flag = True
        if self.sm.current == "main":
            screen = self.sm.current_screen
            if self.popup_is_open:
                if (
                    codepoint == "a"
                    or codepoint == "0"
                    or codepoint == "1"
                    or codepoint == "2"
                    or codepoint == "3"
                    or codepoint == "4"
                ):
                    screen.dismiss_popup()
                elif keycode == 13:
                    screen.dismiss_popup()
                else:
                    return_flag = False
            else:
                if codepoint == "a":
                    screen.ids["main_image_view"].get_images(-1)
                elif codepoint == "0":
                    screen.ids["main_image_view"].get_images(0)
                elif codepoint == "1":
                    screen.ids["main_image_view"].get_images(1)
                elif codepoint == "2":
                    screen.ids["main_image_view"].get_images(2)
                elif codepoint == "3":
                    screen.ids["main_image_view"].get_images(3)
                elif codepoint == "4":
                    screen.ids["main_image_view"].get_images(4)
                elif keycode == 13:
                    screen.ids["main_image_view"].get_images(-1)
                else:
                    return_flag = False

        elif self.sm.current == "making_dataset":
            screen = self.sm.current_screen
            if codepoint == "a":
                screen.ids["dataset_image_view"].save_images(0)
            elif codepoint == "b":
                screen.ids["dataset_image_view"].save_images(1)
        else:
            return_flag = False
        return return_flag

    def get_cameras(self):
        self.camera_count = 0
        for i in range(0, 5):
            index_name = "use_camera_" + str(i)
            if self.confini["settings"][index_name] == "True":
                cap = cv2.VideoCapture(i + cv2.CAP_DSHOW)
                if cap.isOpened():
                    camera_para = {
                        "NUMBER": i,
                        "NAME": "Camera " + str(i),
                        "ACTIVE": True,
                        "SELECTED": False,
                        "CAP_PROP_FRAME_WIDTH": cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                        "CAP_PROP_FRAME_HEIGHT": cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
                        "CAP_PROP_FPS": cap.get(cv2.CAP_PROP_FPS),
                        "CAP_PROP_BRIGHTNESS": cap.get(cv2.CAP_PROP_BRIGHTNESS),
                        "CAP_PROP_CONTRAST": cap.get(cv2.CAP_PROP_CONTRAST),
                        "CAP_PROP_SATURATION": cap.get(cv2.CAP_PROP_SATURATION),
                        "CAP_PROP_HUE": cap.get(cv2.CAP_PROP_HUE),
                        "CAP_PROP_GAIN": cap.get(cv2.CAP_PROP_GAIN),
                        "CAP_PROP_GAMMA": cap.get(cv2.CAP_PROP_GAMMA),
                        "CAP_PROP_EXPOSURE": cap.get(cv2.CAP_PROP_EXPOSURE),
                        "CAP_PROP_FOCUS": cap.get(cv2.CAP_PROP_FOCUS),
                        "CAP_PROP_WB_TEMPERATURE": cap.get(cv2.CAP_PROP_WB_TEMPERATURE),
                    }
                    editable_para = {
                        "EDIT_FRAME_WIDTH": cap.set(
                            cv2.CAP_PROP_FRAME_WIDTH,
                            camera_para["CAP_PROP_FRAME_WIDTH"],
                        ),
                        "EDIT_FRAME_HEIGHT": cap.set(
                            cv2.CAP_PROP_FRAME_HEIGHT,
                            camera_para["CAP_PROP_FRAME_HEIGHT"],
                        ),
                        "EDIT_FPS": cap.set(
                            cv2.CAP_PROP_FPS, camera_para["CAP_PROP_FPS"]
                        ),
                        "EDIT_BRIGHTNESS": cap.set(
                            cv2.CAP_PROP_BRIGHTNESS, camera_para["CAP_PROP_BRIGHTNESS"]
                        ),
                        "EDIT_CONTRAST": cap.set(
                            cv2.CAP_PROP_CONTRAST, camera_para["CAP_PROP_CONTRAST"]
                        ),
                        "EDIT_SATURATION": cap.set(
                            cv2.CAP_PROP_SATURATION, camera_para["CAP_PROP_SATURATION"]
                        ),
                        "EDIT_HUE": cap.set(
                            cv2.CAP_PROP_HUE, camera_para["CAP_PROP_HUE"]
                        ),
                        "EDIT_GAIN": cap.set(
                            cv2.CAP_PROP_GAIN, camera_para["CAP_PROP_GAIN"]
                        ),
                        "EDIT_GAMMA": cap.set(
                            cv2.CAP_PROP_GAMMA, camera_para["CAP_PROP_GAMMA"]
                        ),
                        "EDIT_EXPOSURE": cap.set(
                            cv2.CAP_PROP_EXPOSURE, camera_para["CAP_PROP_EXPOSURE"]
                        ),
                        "EDIT_AUTO_EXPOSURE": cap.set(
                            cv2.CAP_PROP_AUTO_EXPOSURE,
                            0.1,
                        ),
                        "EDIT_FOCUS": cap.set(
                            cv2.CAP_PROP_FOCUS, camera_para["CAP_PROP_FOCUS"]
                        ),
                        "EDIT_AUTOFOCUS": cap.set(cv2.CAP_PROP_AUTOFOCUS, 0.1),
                        "EDIT_AUTO_WB": cap.set(cv2.CAP_PROP_AUTO_WB, 0.1),
                        "EDIT_WB_TEMPERATURE": cap.set(
                            cv2.CAP_PROP_WB_TEMPERATURE,
                            camera_para["CAP_PROP_WB_TEMPERATURE"],
                        ),
                    }
                    camera_para.update(editable_para)
                    update_auto_para = {
                        "CAP_PROP_AUTO_EXPOSURE": cap.get(cv2.CAP_PROP_AUTO_EXPOSURE),
                        "CAP_PROP_AUTOFOCUS": cap.get(cv2.CAP_PROP_AUTOFOCUS),
                        "CAP_PROP_AUTO_WB": cap.get(cv2.CAP_PROP_AUTO_WB),
                    }
                    camera_para.update(update_auto_para)
                    self.camera_parameter_list[i] = camera_para
                    self.camera_list[i] = cap
                    self.camera_count += 1

    def add_screens(self):
        self.sm.add_widget(CameraSettingScreen(name="camera_setting"))
        self.sm.add_widget(TargetAreaScreen(name="target_area"))
        self.sm.add_widget(PreprocessingScreen(name="preprocessing"))
        self.sm.add_widget(InspectionSettingScreen(name="inspection_setting"))
        self.sm.add_widget(MakingDatasetScreen(name="making_dataset"))
        self.sm.add_widget(AimodelSettingScreen(name="aimodel_setting"))
        self.sm.add_widget(MainScreen(name="main"))

    def start_cs_screen(self, lang):
        self.lang = lang
        self.add_screens()
        path_list = glob.glob("./adfi_client_app_data/inspection_data/*.pkl")
        self.sm.transition.direction = "left"
        if len(path_list) > 0:
            self.sm.current = "main"
        else:
            self.sm.current = "camera_setting"

    def resize_cv_image(self, cv_image, size_max=(650, 500)):
        if cv_image is not None:
            height = cv_image.shape[0]
            width = cv_image.shape[1]
            x_ratio = 1.0
            y_ratio = 1.0
            if size_max[0] < width:
                x_ratio = size_max[0] / width
            if size_max[1] < height:
                y_ratio = size_max[1] / height
            if x_ratio < y_ratio:
                resize_size = (size_max[0], round(height * x_ratio))
                cv_image = cv2.resize(cv_image, resize_size)
            if x_ratio > y_ratio:
                resize_size = (round(width * y_ratio), size_max[1])
                cv_image = cv2.resize(cv_image, resize_size)
        return cv_image

    def crop_image_ratio(self, cv_image, ratio1, ratio2):
        ret_image = cv_image
        if ratio1 is not None and ratio2 is not None:
            height = cv_image.shape[0]
            width = cv_image.shape[1]
            x_coord = [int(ratio1[0] * width), int(ratio2[0] * width)]
            y_coord = [int((1 - ratio1[1]) * height), int((1 - ratio2[1]) * height)]
            if x_coord[0] != x_coord[1] and y_coord[0] != y_coord[1]:
                ret_image = cv_image[
                    min(y_coord) : max(y_coord), min(x_coord) : max(x_coord)
                ]
        return ret_image

    def set_resolution_and_fps(self):
        for i in range(0, 5):
            cap = self.camera_list[i]
            if cap is not None and cap.isOpened():
                index_name = "camera_" + str(i)
                width = self.confini["settings"][index_name + "_width"]
                height = self.confini["settings"][index_name + "_height"]
                fps = self.confini["settings"][index_name + "_fps"]
                if str.isdecimal(width):
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
                if str.isdecimal(height):
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
                if str.isdecimal(fps):
                    cap.set(cv2.CAP_PROP_FPS, int(fps))
                param_dict = {
                    "CAP_PROP_FRAME_WIDTH": cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                    "CAP_PROP_FRAME_HEIGHT": cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
                    "CAP_PROP_FPS": cap.get(cv2.CAP_PROP_FPS),
                }
                self.camera_parameter_list[i].update(param_dict)

    def open_cameras(self, use_camera_list=list(range(5))):
        for i in range(0, 5):
            if self.camera_list[i] is not None:
                self.camera_list[i].release()
                self.camera_list[i] = None
            index_name = "use_camera_" + str(i)
            if self.confini["settings"][index_name] == "True" and i in use_camera_list:
                cap = cv2.VideoCapture(i + cv2.CAP_DSHOW)
                if cap.isOpened():
                    self.camera_list[i] = cap
        self.set_resolution_and_fps()
        self.camera_load_flg = False

    def release_cameras(self):
        for i in range(0, 5):
            if self.camera_list[i] is not None:
                self.camera_list[i].release()
                self.camera_list[i] = None
        self.camera_load_flg = False

    def open_inspection_cameras(self):
        use_camera_list = []
        current_inspection_dir = "./adfi_client_app_data/current_inspection"
        path_list = glob.glob(current_inspection_dir + "/*.pkl")
        if len(path_list) > 0 and os.path.exists(path_list[0]):
            with open(path_list[0], "rb") as f:
                self.current_inspection_dict = pickle.load(f)

            settings_list = self.current_inspection_dict["PREPROCESSING_LIST"]
            if len(settings_list) > 0:
                for settings_dict in settings_list:
                    if int(settings_dict["CAMERA_NUM"]) not in use_camera_list:
                        use_camera_list.append(int(settings_dict["CAMERA_NUM"]))
                self.open_cameras(use_camera_list=use_camera_list)

                for camera_num in use_camera_list:
                    camera_filename = (
                        self.camera_param_dir
                        + "/camera_"
                        + str(camera_num)
                        + "_parameter.pkl"
                    )
                    if self.camera_list[camera_num] is not None:
                        if os.path.exists(camera_filename):
                            with open(camera_filename, "rb") as f:
                                camera_param_dict = pickle.load(f)
                            if camera_param_dict["EDIT_BRIGHTNESS"]:
                                self.camera_list[camera_num].set(
                                    cv2.CAP_PROP_BRIGHTNESS,
                                    camera_param_dict["CAP_PROP_BRIGHTNESS"],
                                )
                            if camera_param_dict["EDIT_CONTRAST"]:
                                self.camera_list[camera_num].set(
                                    cv2.CAP_PROP_CONTRAST,
                                    camera_param_dict["CAP_PROP_CONTRAST"],
                                )
                            if camera_param_dict["EDIT_SATURATION"]:
                                self.camera_list[camera_num].set(
                                    cv2.CAP_PROP_SATURATION,
                                    camera_param_dict["CAP_PROP_SATURATION"],
                                )
                            if camera_param_dict["EDIT_HUE"]:
                                self.camera_list[camera_num].set(
                                    cv2.CAP_PROP_HUE, camera_param_dict["CAP_PROP_HUE"]
                                )
                            if camera_param_dict["EDIT_GAIN"]:
                                self.camera_list[camera_num].set(
                                    cv2.CAP_PROP_GAIN,
                                    camera_param_dict["CAP_PROP_GAIN"],
                                )
                            if camera_param_dict["EDIT_GAMMA"]:
                                self.camera_list[camera_num].set(
                                    cv2.CAP_PROP_GAMMA,
                                    camera_param_dict["CAP_PROP_GAMMA"],
                                )
                            if camera_param_dict["EDIT_EXPOSURE"]:
                                self.camera_list[camera_num].set(
                                    cv2.CAP_PROP_EXPOSURE,
                                    camera_param_dict["CAP_PROP_EXPOSURE"],
                                )
                            if camera_param_dict["EDIT_AUTO_EXPOSURE"]:
                                self.camera_list[camera_num].set(
                                    cv2.CAP_PROP_AUTO_EXPOSURE,
                                    camera_param_dict["CAP_PROP_AUTO_EXPOSURE"],
                                )
                            if camera_param_dict["EDIT_FOCUS"]:
                                self.camera_list[camera_num].set(
                                    cv2.CAP_PROP_FOCUS,
                                    camera_param_dict["CAP_PROP_FOCUS"],
                                )
                            if camera_param_dict["EDIT_AUTOFOCUS"]:
                                self.camera_list[camera_num].set(
                                    cv2.CAP_PROP_AUTOFOCUS,
                                    camera_param_dict["CAP_PROP_AUTOFOCUS"],
                                )
                            if camera_param_dict["EDIT_AUTO_WB"]:
                                self.camera_list[camera_num].set(
                                    cv2.CAP_PROP_AUTO_WB,
                                    camera_param_dict["CAP_PROP_AUTO_WB"],
                                )
                            if "RATIO_1" in camera_param_dict:
                                self.current_ratio1[camera_num] = camera_param_dict[
                                    "RATIO_1"
                                ]
                            if "RATIO_2" in camera_param_dict:
                                self.current_ratio2[camera_num] = camera_param_dict[
                                    "RATIO_2"
                                ]
                    else:
                        toast(
                            "Camera "
                            + str(camera_num)
                            + " : "
                            + self.textini[self.lang]["app_toast_no_camera_message"]
                        )
        else:
            toast(self.textini[self.lang]["app_toast_no_inspection_message"])

    def popup_open(self, *args):
        content = QuitPopupMenu(popup_close=self.popup_close)
        self.popup = Popup(
            title=self.textini[self.lang]["adfi_app_name"],
            content=content,
            size_hint=(0.3, 0.3),
            auto_dismiss=False,
        )
        self.popup.open()
        return True

    def popup_close(self):
        self.popup.dismiss()

    def stop_app(self):
        for cap in self.camera_list:
            if cap is not None:
                cap.release()
        self.stop()


if __name__ == "__main__":
    InspectionApp().run()
