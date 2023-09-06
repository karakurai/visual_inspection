import os
import pickle

import cv2
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.screen import MDScreen


class CameraSettingScreen(MDScreen):
    def __init__(self, **kwargs):
        super(CameraSettingScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self):
        if self.app.camera_count == 0:
            self.ids["message"].text = self.app.textini[self.app.lang]["cs_camera_no"]

        for camera_para in self.app.camera_parameter_list:
            if camera_para is not None:
                if camera_para["NUMBER"] == 0:
                    self.ids["cb0"].text = (
                        camera_para["NAME"]
                        + ": "
                        + self.app.textini[self.app.lang]["available"]
                    )
                    self.ids["cb0"].disabled = False
                if camera_para["NUMBER"] == 1:
                    self.ids["cb1"].text = (
                        camera_para["NAME"]
                        + ": "
                        + self.app.textini[self.app.lang]["available"]
                    )
                    self.ids["cb1"].disabled = False
                if camera_para["NUMBER"] == 2:
                    self.ids["cb2"].text = (
                        camera_para["NAME"]
                        + ": "
                        + self.app.textini[self.app.lang]["available"]
                    )
                    self.ids["cb2"].disabled = False
                if camera_para["NUMBER"] == 3:
                    self.ids["cb3"].text = (
                        camera_para["NAME"]
                        + ": "
                        + self.app.textini[self.app.lang]["available"]
                    )
                    self.ids["cb3"].disabled = False
                if camera_para["NUMBER"] == 4:
                    self.ids["cb4"].text = (
                        camera_para["NAME"]
                        + ": "
                        + self.app.textini[self.app.lang]["available"]
                    )
                    self.ids["cb4"].disabled = False
        if self.app.camera_num is not None:
            self.ids["camera_view"].active_camera(self.app.camera_num)
            self.ids["parameter_table"].display_parameter(self.app.camera_num)
        if not self.app.camera_load_flg:
            for i in range(0, 5):
                self.load_camera_parameter(i)
            self.app.camera_load_flg = True

    def load_camera_parameter(self, camera_num):
        tmp_cap = self.app.camera_list[camera_num]
        if tmp_cap is not None:
            filename = (
                self.app.camera_param_dir
                + "/camera_"
                + str(camera_num)
                + "_parameter.pkl"
            )
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    camera_param_dict = pickle.load(f)
                if camera_param_dict["EDIT_BRIGHTNESS"]:
                    tmp_cap.set(
                        cv2.CAP_PROP_BRIGHTNESS,
                        camera_param_dict["CAP_PROP_BRIGHTNESS"],
                    )
                if camera_param_dict["EDIT_CONTRAST"]:
                    tmp_cap.set(
                        cv2.CAP_PROP_CONTRAST, camera_param_dict["CAP_PROP_CONTRAST"]
                    )
                if camera_param_dict["EDIT_SATURATION"]:
                    tmp_cap.set(
                        cv2.CAP_PROP_SATURATION,
                        camera_param_dict["CAP_PROP_SATURATION"],
                    )
                if camera_param_dict["EDIT_HUE"]:
                    tmp_cap.set(cv2.CAP_PROP_HUE, camera_param_dict["CAP_PROP_HUE"])
                if camera_param_dict["EDIT_GAIN"]:
                    tmp_cap.set(cv2.CAP_PROP_GAIN, camera_param_dict["CAP_PROP_GAIN"])
                if camera_param_dict["EDIT_GAMMA"]:
                    tmp_cap.set(cv2.CAP_PROP_GAMMA, camera_param_dict["CAP_PROP_GAMMA"])
                if camera_param_dict["EDIT_EXPOSURE"]:
                    tmp_cap.set(
                        cv2.CAP_PROP_EXPOSURE, camera_param_dict["CAP_PROP_EXPOSURE"]
                    )
                if camera_param_dict["EDIT_AUTO_EXPOSURE"]:
                    tmp_cap.set(
                        cv2.CAP_PROP_AUTO_EXPOSURE,
                        camera_param_dict["CAP_PROP_AUTO_EXPOSURE"],
                    )
                if camera_param_dict["EDIT_FOCUS"]:
                    tmp_cap.set(cv2.CAP_PROP_FOCUS, camera_param_dict["CAP_PROP_FOCUS"])
                if camera_param_dict["EDIT_AUTOFOCUS"]:
                    tmp_cap.set(
                        cv2.CAP_PROP_AUTOFOCUS, camera_param_dict["CAP_PROP_AUTOFOCUS"]
                    )
                if camera_param_dict["EDIT_AUTO_WB"]:
                    tmp_cap.set(
                        cv2.CAP_PROP_AUTO_WB, camera_param_dict["CAP_PROP_AUTO_WB"]
                    )
                if camera_param_dict["EDIT_WB_TEMPERATURE"]:
                    tmp_cap.set(
                        cv2.CAP_PROP_WB_TEMPERATURE,
                        camera_param_dict["CAP_PROP_WB_TEMPERATURE"],
                    )
                return True
        return False

    def button_bg_color(self, camera_num):
        default_color = 0.2, 0.2, 0.2, 1
        color = "purple"
        self.ids["cb0"].md_bg_color = default_color
        self.ids["cb1"].md_bg_color = default_color
        self.ids["cb2"].md_bg_color = default_color
        self.ids["cb3"].md_bg_color = default_color
        self.ids["cb4"].md_bg_color = default_color
        if camera_num == 0:
            self.ids["cb0"].md_bg_color = color
        if camera_num == 1:
            self.ids["cb1"].md_bg_color = color
        if camera_num == 2:
            self.ids["cb2"].md_bg_color = color
        if camera_num == 3:
            self.ids["cb3"].md_bg_color = color
        if camera_num == 4:
            self.ids["cb4"].md_bg_color = color


class CameraView(MDFloatLayout):
    def __init__(self, **kwargs):
        super(CameraView, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.active_flg = False
        self.frame = None
        self.cap = None
        self.texture = None
        self.pt = None
        self.screen = None
        self.delete_settings_dialog = None

    def active_camera(self, camera_num):
        self.active_flg = self.app.camera_parameter_list[camera_num]["ACTIVE"]
        self.screen = self.app.sm.get_screen("camera_setting")
        self.pt = self.screen.ids["parameter_table"]
        if self.cap is not None or not self.active_flg:
            self.clock_unschedule()
            self.screen.ids["parameter_settings_button"].disabled = True
            self.screen.ids["save_settings_button"].disabled = True
            self.screen.ids["delete_saved_settings_button"].disabled = True
        if self.active_flg:
            self.cap = self.app.camera_list[camera_num]
            self.app.camera_num = camera_num
            self.screen.ids["parameter_settings_button"].disabled = False
            self.screen.ids["save_settings_button"].disabled = False
            self.screen.ids["delete_saved_settings_button"].disabled = False
            Clock.schedule_interval(
                self.update, 1.0 / float(self.app.confini["settings"]["display_fps"])
            )
            Clock.schedule_interval(self.update_parameter, 5)
            Clock.schedule_interval(
                self._disp_canvas,
                1.0 / float(self.app.confini["settings"]["display_fps"]),
            )

    def _disp_canvas(self, dt):
        if self.texture is not None:
            self.canvas.before.clear()
            self.canvas.before.add(Color(rgb=[1, 1, 1]))
            self.canvas.before.add(
                Rectangle(texture=self.texture, pos=self.pos, size=self.texture.size)
            )

    def clock_unschedule(self):
        Clock.unschedule(self.update)
        Clock.unschedule(self.update_parameter)
        Clock.unschedule(self._disp_canvas)

    def camera_setting(self):
        if self.cap is not None:
            self.cap.set(cv2.CAP_PROP_SETTINGS, 1)

    def save_camera_parameter(self):
        if self.cap is not None and self.app.camera_num is not None:
            save_dir = self.app.camera_param_dir
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            param_dict = self.app.camera_parameter_list[self.app.camera_num]
            filename = "camera_" + str(self.app.camera_num) + "_parameter.pkl"
            with open(save_dir + "/" + filename, "wb") as f:
                pickle.dump(param_dict, f)
            toast(self.app.textini[self.app.lang]["cs_toast_save_message"])
        else:
            toast(self.app.textini[self.app.lang]["cs_toast_ng_save_message"])

    def delete_saved_camera_parameter(self):
        if self.cap is not None:
            filename = (
                self.app.camera_param_dir
                + "/camera_"
                + str(self.app.camera_num)
                + "_parameter.pkl"
            )
            if os.path.exists(filename):
                os.remove(filename)
                toast(
                    self.app.textini[self.app.lang][
                        "cs_toast_delete_saved_setteings_message"
                    ]
                )
            else:
                toast(
                    self.app.textini[self.app.lang][
                        "cs_toast_delete_saved_setteings_ng_message"
                    ]
                )
        if self.delete_settings_dialog is not None:
            self.delete_settings_dialog.dismiss()

    def show_delete_settings_dialog(self):
        self.delete_settings_dialog = MDDialog(
            text=self.app.textini[self.app.lang]["cs_dialog_delete_setteings_message"],
            buttons=[
                MDFlatButton(
                    text=self.app.textini[self.app.lang]["cansel"],
                    text_color=self.app.theme_cls.primary_color,
                    on_release=lambda x: self.delete_settings_dialog.dismiss(),
                ),
                MDFlatButton(
                    text=self.app.textini[self.app.lang]["delete"],
                    text_color=self.app.theme_cls.primary_color,
                    on_release=lambda x: self.delete_saved_camera_parameter(),
                ),
            ],
        )
        self.delete_settings_dialog.open()

    def update(self, dt):
        if self.active_flg:
            ret, tmp_frame = self.cap.read()
            if not ret:
                return
            self.frame = self.app.resize_cv_image(tmp_frame)
            flip_frame = cv2.flip(self.frame, 0)
            if flip_frame is not None:
                buf = flip_frame.tobytes()
                texture = Texture.create(
                    size=(self.frame.shape[1], self.frame.shape[0]),
                    colorfmt="bgr",
                )
                texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
                self.texture = texture

    def update_parameter(self, dt):
        if self.cap.isOpened():
            camera_para = {
                "NUMBER": self.app.camera_num,
                "NAME": "Camera " + str(self.app.camera_num),
                "ACTIVE": True,
                "SELECTED": False,
                "CAP_PROP_FRAME_WIDTH": self.cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                "CAP_PROP_FRAME_HEIGHT": self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
                "CAP_PROP_FPS": self.cap.get(cv2.CAP_PROP_FPS),
                "CAP_PROP_BRIGHTNESS": self.cap.get(cv2.CAP_PROP_BRIGHTNESS),
                "CAP_PROP_CONTRAST": self.cap.get(cv2.CAP_PROP_CONTRAST),
                "CAP_PROP_SATURATION": self.cap.get(cv2.CAP_PROP_SATURATION),
                "CAP_PROP_HUE": self.cap.get(cv2.CAP_PROP_HUE),
                "CAP_PROP_GAIN": self.cap.get(cv2.CAP_PROP_GAIN),
                "CAP_PROP_GAMMA": self.cap.get(cv2.CAP_PROP_GAMMA),
                "CAP_PROP_EXPOSURE": self.cap.get(cv2.CAP_PROP_EXPOSURE),
                "CAP_PROP_AUTO_EXPOSURE": self.cap.get(cv2.CAP_PROP_AUTO_EXPOSURE),
                "CAP_PROP_FOCUS": self.cap.get(cv2.CAP_PROP_FOCUS),
                "CAP_PROP_AUTOFOCUS": self.cap.get(cv2.CAP_PROP_AUTOFOCUS),
                "CAP_PROP_AUTO_WB": self.cap.get(cv2.CAP_PROP_AUTO_WB),
                "CAP_PROP_WB_TEMPERATURE": self.cap.get(cv2.CAP_PROP_WB_TEMPERATURE),
            }
            self.app.camera_parameter_list[self.app.camera_num].update(camera_para)
            self.pt.display_parameter(None)


class ParameterTable(MDGridLayout):
    def __init__(self, **kwargs):
        super(ParameterTable, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def display_parameter(self, camera_num):
        self.screen = self.app.sm.get_screen("camera_setting")
        if camera_num is None:
            camera_num = self.app.camera_num
        camera_parameter_list = self.app.camera_parameter_list
        if camera_num is None or camera_parameter_list[camera_num] is None:
            self.screen.ids["camera_name"].text = ""
            self.screen.ids["param_width"].text = ""
            self.screen.ids["param_height"].text = ""
            self.screen.ids["param_auto_focus"].text = ""
            self.screen.ids["param_focus"].text = ""
            self.screen.ids["param_auto_exposure"].text = ""
            self.screen.ids["param_exposure"].text = ""
            self.screen.ids["param_gamma"].text = ""
            self.screen.ids["param_gain"].text = ""
        else:
            self.screen.ids["camera_name"].text = "Camera " + str(camera_num)
            self.screen.ids["param_width"].text = str(
                camera_parameter_list[camera_num]["CAP_PROP_FRAME_WIDTH"]
            )
            self.screen.ids["param_height"].text = str(
                camera_parameter_list[camera_num]["CAP_PROP_FRAME_HEIGHT"]
            )
            self.screen.ids["param_auto_focus"].text = (
                str(camera_parameter_list[camera_num]["CAP_PROP_AUTOFOCUS"])
                if camera_parameter_list[camera_num]["EDIT_AUTOFOCUS"]
                else self.app.textini[self.app.lang]["non_editable"]
            )
            self.screen.ids["param_focus"].text = str(
                camera_parameter_list[camera_num]["CAP_PROP_FOCUS"]
                if camera_parameter_list[camera_num]["EDIT_FOCUS"]
                else self.app.textini[self.app.lang]["non_editable"]
            )
            self.screen.ids["param_auto_exposure"].text = str(
                camera_parameter_list[camera_num]["CAP_PROP_AUTO_EXPOSURE"]
                if camera_parameter_list[camera_num]["EDIT_AUTO_EXPOSURE"]
                else self.app.textini[self.app.lang]["non_editable"]
            )
            self.screen.ids["param_exposure"].text = str(
                camera_parameter_list[camera_num]["CAP_PROP_EXPOSURE"]
                if camera_parameter_list[camera_num]["EDIT_EXPOSURE"]
                else self.app.textini[self.app.lang]["non_editable"]
            )
            self.screen.ids["param_gamma"].text = str(
                camera_parameter_list[camera_num]["CAP_PROP_GAMMA"]
                if camera_parameter_list[camera_num]["EDIT_GAMMA"]
                else self.app.textini[self.app.lang]["non_editable"]
            )
            self.screen.ids["param_gain"].text = str(
                camera_parameter_list[camera_num]["CAP_PROP_GAIN"]
                if camera_parameter_list[camera_num]["EDIT_GAIN"]
                else self.app.textini[self.app.lang]["non_editable"]
            )
