import os
import pickle

import cv2
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle
from kivy.graphics.texture import Texture
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen


class TargetAreaScreen(MDScreen):
    def __init__(self, **kwargs):
        super(TargetAreaScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self):
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
            self.ids["image_view"].active_camera(self.app.camera_num)


class ImageView(MDFloatLayout):
    def __init__(self, **kwargs):
        super(ImageView, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.active_flg = False
        self.frame = None
        self.cap = None
        self.tmp_texture = None
        self.screen = None
        self.update_count = 0
        self.pos = (200, 200)
        self.touch_down = None
        self.touch_up = None
        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None
        self.ratio1 = None
        self.ratio2 = None
        self.delete_area_dialog = None
        self.save_area_dialog = None
        self.pause_flg = False

    def active_camera(self, camera_num):
        self.active_flg = self.app.camera_parameter_list[camera_num]["ACTIVE"]
        self.screen = self.app.sm.get_screen("target_area")
        if self.cap is not None or not self.active_flg:
            self.screen.ids["save_area_button"].disabled = True
            self.screen.ids["delete_saved_area_button"].disabled = True
            self.clock_unschedule()
        if self.active_flg:
            self.cap = self.app.camera_list[camera_num]
            self.app.camera_num = camera_num
            self.touch_down = None
            self.touch_up = None
            self.x1 = None
            self.y1 = None
            self.x2 = None
            self.y2 = None
            self.screen.ids["save_area_button"].disabled = False
            self.screen.ids["delete_saved_area_button"].disabled = False
            self.screen.ids["camera_name"].text = "Camera " + str(camera_num)
            self.load_camera_parameter()
            self.update_count = 0
            Clock.schedule_interval(self.clock_capture, 1.0 / float(self.app.confini["settings"]["display_fps"]))
            Clock.schedule_interval(self._disp_canvas, 1.0 / float(self.app.confini["settings"]["display_fps"]))

    def clock_unschedule(self):
        Clock.unschedule(self.clock_capture)
        Clock.unschedule(self._disp_canvas)

    def load_camera_parameter(self):
        if self.cap is not None:
            filename = (
                self.app.camera_param_dir
                + "/camera_"
                + str(self.app.camera_num)
                + "_parameter.pkl"
            )
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    camera_param_dict = pickle.load(f)
                if camera_param_dict["EDIT_BRIGHTNESS"]:
                    self.cap.set(
                        cv2.CAP_PROP_BRIGHTNESS,
                        camera_param_dict["CAP_PROP_BRIGHTNESS"],
                    )
                if camera_param_dict["EDIT_CONTRAST"]:
                    self.cap.set(
                        cv2.CAP_PROP_CONTRAST, camera_param_dict["CAP_PROP_CONTRAST"]
                    )
                if camera_param_dict["EDIT_SATURATION"]:
                    self.cap.set(
                        cv2.CAP_PROP_SATURATION,
                        camera_param_dict["CAP_PROP_SATURATION"],
                    )
                if camera_param_dict["EDIT_HUE"]:
                    self.cap.set(cv2.CAP_PROP_HUE, camera_param_dict["CAP_PROP_HUE"])
                if camera_param_dict["EDIT_GAIN"]:
                    self.cap.set(cv2.CAP_PROP_GAIN, camera_param_dict["CAP_PROP_GAIN"])
                if camera_param_dict["EDIT_GAMMA"]:
                    self.cap.set(
                        cv2.CAP_PROP_GAMMA, camera_param_dict["CAP_PROP_GAMMA"]
                    )
                if camera_param_dict["EDIT_EXPOSURE"]:
                    self.cap.set(
                        cv2.CAP_PROP_EXPOSURE, camera_param_dict["CAP_PROP_EXPOSURE"]
                    )
                if camera_param_dict["EDIT_AUTO_EXPOSURE"]:
                    self.cap.set(
                        cv2.CAP_PROP_AUTO_EXPOSURE,
                        camera_param_dict["CAP_PROP_AUTO_EXPOSURE"],
                    )
                if camera_param_dict["EDIT_FOCUS"]:
                    self.cap.set(
                        cv2.CAP_PROP_FOCUS, camera_param_dict["CAP_PROP_FOCUS"]
                    )
                if camera_param_dict["EDIT_AUTOFOCUS"]:
                    self.cap.set(
                        cv2.CAP_PROP_AUTOFOCUS, camera_param_dict["CAP_PROP_AUTOFOCUS"]
                    )
                if "RATIO_1" in camera_param_dict:
                    self.ratio1 = camera_param_dict["RATIO_1"]
                if "RATIO_2" in camera_param_dict:
                    self.ratio2 = camera_param_dict["RATIO_2"]
                return True
        return False

    def clock_capture(self, dt):
        if self.active_flg:
            ret, tmp_frame = self.cap.read()
            if not ret:
                return
            if not self.pause_flg:
                self.frame = self.app.resize_cv_image(tmp_frame)
                flip_frame = cv2.flip(self.frame, 0)
                if flip_frame is not None:
                    buf = flip_frame.tobytes()
                    texture = Texture.create(
                        size=(self.frame.shape[1], self.frame.shape[0]),
                        colorfmt="bgr",
                    )
                    texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
                    self.tmp_texture = texture
                    if self.update_count == 0:
                        self.load_area()
                    self.update_count += 1

    def pause(self):
        if self.pause_flg:
            self.pause_flg = False
            self.screen.ids["pause_button"].text = self.app.textini[self.app.lang][
                "ta_pause"
            ]
        else:
            self.pause_flg = True
            self.screen.ids["pause_button"].text = self.app.textini[self.app.lang][
                "ta_start"
            ]

    def _disp_canvas(self, dt):
        if self.tmp_texture is not None:
            self.canvas.before.clear()
            self.canvas.before.add(Color(rgb=[1, 1, 1]))
            self.canvas.before.add(
                Rectangle(
                    texture=self.tmp_texture, pos=self.pos, size=self.tmp_texture.size
                )
            )
            if self.x1 is None:
                self.x1 = self.pos[0]
            if self.y1 is None:
                self.y1 = self.pos[1]
            if self.x2 is None:
                self.x2 = self.tmp_texture.size[0] + self.pos[0]
            if self.y2 is None:
                self.y2 = self.tmp_texture.size[1] + self.pos[1]
            if self.touch_down is not None and self.touch_up is not None:
                self.x1 = self.touch_down[0]
                self.y1 = self.touch_down[1]
                self.x2 = self.touch_up[0]
                self.y2 = self.touch_up[1]
            self.ratio1 = self._change_coord_to_ratio(
                [self.x1 - self.pos[0], self.y1 - self.pos[1]], self.tmp_texture.size
            )
            self.ratio2 = self._change_coord_to_ratio(
                [self.x2 - self.pos[0], self.y2 - self.pos[1]], self.tmp_texture.size
            )
            self.screen.ids["x1"].text = str(self.ratio1[0])
            self.screen.ids["y1"].text = str(self.ratio1[1])
            self.screen.ids["x2"].text = str(self.ratio2[0])
            self.screen.ids["y2"].text = str(self.ratio2[1])
            if self._check_ratio(self.ratio1, self.ratio2):
                self.screen.ids["save_area_button"].disabled = False
                self.canvas.before.add(Color(rgb=[1, 0.2, 0.2]))
                self.canvas.before.add(
                    Line(
                        rectangle=(
                            self.x1,
                            self.y1,
                            self.x2 - self.x1,
                            self.y2 - self.y1,
                        ),
                        width=2,
                    )
                )
            else:
                self.screen.ids["save_area_button"].disabled = True
                self.canvas.before.add(Color(rgb=[0.4, 0.4, 0.4]))
                self.canvas.before.add(
                    Line(
                        rectangle=(
                            self.x1,
                            self.y1,
                            self.x2 - self.x1,
                            self.y2 - self.y1,
                        ),
                        width=2,
                    )
                )

    def _check_ratio(self, ratio1, ratio2):
        ret_flg = True
        if abs(ratio1[0] - ratio2[0]) < 0.1 or abs(ratio1[1] - ratio2[1]) < 0.1:
            ret_flg = False
        return ret_flg

    def _change_coord_to_ratio(self, coordinate, texture_size, digit=3):
        width_ratio = round(int(coordinate[0]) / int(texture_size[0]), digit)
        height_ratio = round(int(coordinate[1]) / int(texture_size[1]), digit)
        return [width_ratio, height_ratio]

    def _change_ratio_to_coord(self, ratio, texture_size):
        return [int(ratio[0] * texture_size[0]), int(ratio[1] * texture_size[1])]

    def _check_pos(self, pos):
        ret_pos = [pos[0], pos[1]]
        if pos[0] < self.pos[0]:
            ret_pos[0] = self.pos[0]
        if pos[0] > self.pos[0] + self.tmp_texture.size[0]:
            ret_pos[0] = self.pos[0] + self.tmp_texture.size[0]
        if pos[1] < self.pos[1]:
            ret_pos[1] = self.pos[1]
        if pos[1] > self.pos[1] + self.tmp_texture.size[1]:
            ret_pos[1] = self.pos[1] + self.tmp_texture.size[1]
        return (int(ret_pos[0]), int(ret_pos[1]))

    def _check_on_canvas(self, pos):
        ret_flg = True
        margin = 20
        if pos[0] < self.pos[0] - margin:
            ret_flg = False
        if pos[0] > self.pos[0] + self.tmp_texture.size[0] + margin:
            ret_flg = False
        if pos[1] < self.pos[1] - margin:
            ret_flg = False
        if pos[1] > self.pos[1] + self.tmp_texture.size[1] + margin:
            ret_flg = False
        return ret_flg

    def on_touch_down(self, touch):
        if self.tmp_texture is not None and self._check_on_canvas(touch.pos):
            self.touch_up = None
            self.touch_down = self._check_pos(touch.pos)

    def on_touch_move(self, touch):
        if self.tmp_texture is not None and self._check_on_canvas(touch.pos):
            self.touch_up = self._check_pos(touch.pos)

    def on_touch_up(self, touch):
        if self.tmp_texture is not None and self._check_on_canvas(touch.pos):
            self.touch_up = self._check_pos(touch.pos)

    def save_area(self):
        if self.cap is not None and self.app.camera_num is not None:
            save_dir = self.app.camera_param_dir
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            update_dict = {"RATIO_1": self.ratio1, "RATIO_2": self.ratio2}
            if self.app.camera_parameter_list[self.app.camera_num] is None:
                self.app.camera_parameter_list[self.app.camera_num] = update_dict
            else:
                self.app.camera_parameter_list[self.app.camera_num].update(update_dict)
            filename = "camera_" + str(self.app.camera_num) + "_parameter.pkl"
            with open(save_dir + "/" + filename, "wb") as f:
                pickle.dump(self.app.camera_parameter_list[self.app.camera_num], f)
            toast(self.app.textini[self.app.lang]["ta_toast_save_message"])
        else:
            toast(self.app.textini[self.app.lang]["ta_toast_ng_save_message"])
        if self.save_area_dialog is not None:
            self.save_area_dialog.dismiss()

    def load_area(self):
        if self.cap is not None:
            filename = (
                self.app.camera_param_dir
                + "/camera_"
                + str(self.app.camera_num)
                + "_parameter.pkl"
            )
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    camera_param_dict = pickle.load(f)
                    if "RATIO_1" in camera_param_dict:
                        self.ratio1 = camera_param_dict["RATIO_1"]
                        coord1 = self._change_ratio_to_coord(
                            self.ratio1, self.tmp_texture.size
                        )
                        self.x1 = coord1[0] + self.pos[0]
                        self.y1 = coord1[1] + self.pos[1]
                    if "RATIO_2" in camera_param_dict:
                        self.ratio2 = camera_param_dict["RATIO_2"]
                        coord2 = self._change_ratio_to_coord(
                            self.ratio2, self.tmp_texture.size
                        )
                        self.x2 = coord2[0] + self.pos[0]
                        self.y2 = coord2[1] + self.pos[1]
                return True
        return False

    def delete_saved_area(self):
        if self.cap is not None:
            filename = (
                self.app.camera_param_dir
                + "/camera_"
                + str(self.app.camera_num)
                + "_parameter.pkl"
            )
            param_dict = self.app.camera_parameter_list[self.app.camera_num]
            param_dict.pop("RATIO_1", None)
            param_dict.pop("RATIO_2", None)
            self.app.camera_parameter_list[self.app.camera_num] = param_dict
            filename = (
                self.app.camera_param_dir
                + "/camera_"
                + str(self.app.camera_num)
                + "_parameter.pkl"
            )
            if os.path.exists(filename):
                with open(filename, "wb") as f:
                    pickle.dump(param_dict, f)
                toast(
                    self.app.textini[self.app.lang][
                        "ta_toast_delete_saved_area_message"
                    ]
                )
            else:
                toast(
                    self.app.textini[self.app.lang][
                        "ta_toast_delete_saved_area_ng_message"
                    ]
                )
            self.touch_down = None
            self.touch_up = None
            self.x1 = None
            self.y1 = None
            self.x2 = None
            self.y2 = None
            self.ratio1 = [0.0, 0.0]
            self.ratio2 = [1.0, 1.0]
        if self.delete_area_dialog is not None:
            self.delete_area_dialog.dismiss()

    def show_delete_area_dialog(self):
        self.delete_area_dialog = MDDialog(
            text=self.app.textini[self.app.lang]["ta_dialog_delete_area_message"],
            buttons=[
                MDFlatButton(
                    text=self.app.textini[self.app.lang]["cansel"],
                    text_color=self.app.theme_cls.primary_color,
                    on_release=lambda x: self.delete_area_dialog.dismiss(),
                ),
                MDFlatButton(
                    text=self.app.textini[self.app.lang]["delete"],
                    text_color=self.app.theme_cls.primary_color,
                    on_release=lambda x: self.delete_saved_area(),
                ),
            ],
        )
        self.delete_area_dialog.open()

    def show_save_area_dialog(self):
        self.save_area_dialog = MDDialog(
            text=self.app.textini[self.app.lang]["ta_dialog_save_area_message"],
            buttons=[
                MDFlatButton(
                    text=self.app.textini[self.app.lang]["cansel"],
                    text_color=self.app.theme_cls.primary_color,
                    on_release=lambda x: self.save_area_dialog.dismiss(),
                ),
                MDFlatButton(
                    text=self.app.textini[self.app.lang]["ok"],
                    text_color=self.app.theme_cls.primary_color,
                    on_release=lambda x: self.save_area(),
                ),
            ],
        )
        self.save_area_dialog.open()
