import datetime
import glob
import os
import pickle
import re

import cv2
from image_processing import ImageProcessing
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen


class PreprocessingScreen(MDScreen):
    def __init__(self, **kwargs):
        super(PreprocessingScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.gray = False
        self.blur_method = None
        self.blur_ksize = 5
        self.bg_sub = False
        self.bg_sub_th = 20
        self.bg_sub_mask = False
        self.invert = False
        self.whitening = 255
        self.blacking = 1
        self.edge_method = None
        self.edge_ksize = 5
        self.binarization = False
        self.binarization_th = 127
        self.real_time_diff = False
        self.real_time_diff_ksize = 5
        self.background_image_list = [None] * 5
        self.save_background_popup = None
        self.tmp_background = None
        self.save_settings_popup = None
        self.load_settings_popup = None
        self.delete_settings_dialog = None
        self._load_background_image_list()

    def finish(self):
        self.app.sm.transition.direction = "left"
        path_list = glob.glob("./adfi_client_app_data/inspection_data/*.pkl")
        if len(path_list) > 0:
            self.app.sm.current = "main"
        else:
            self.app.sm.current = "inspection_setting"

    def show_delete_settings_dialog(self, delete_filename, delete_name):
        if delete_filename is None or delete_name is None:
            toast(self.app.textini[self.app.lang]["pp_toast_no_checkbox_message"])
        else:
            self.delete_settings_dialog = MDDialog(
                text=self.app.textini[self.app.lang]["pp_dialog_delete_message"]
                + "\n\n"
                + self.app.textini[self.app.lang]["name"]
                + ": "
                + delete_name,
                buttons=[
                    MDFlatButton(
                        text=self.app.textini[self.app.lang]["cansel"],
                        text_color=self.app.theme_cls.primary_color,
                        on_release=lambda x: self.delete_settings_dialog.dismiss(),
                    ),
                    MDFlatButton(
                        text=self.app.textini[self.app.lang]["delete"],
                        text_color=self.app.theme_cls.primary_color,
                        on_release=lambda x: self.delete_settings(delete_filename),
                    ),
                ],
            )
            self.delete_settings_dialog.open()

    def delete_settings(self, delete_filename):
        delete_dir = "./adfi_client_app_data/preprocessing_data"
        file_path = delete_dir + "/" + delete_filename + ".pkl"
        if os.path.exists(file_path):
            os.remove(file_path)
        bg_image_path = delete_dir + "/" + delete_filename + ".png"
        if os.path.exists(bg_image_path):
            os.remove(bg_image_path)
        toast(self.app.textini[self.app.lang]["pp_toast_delete_message"])
        self.load_settings_popup_close()
        self.delete_settings_dialog.dismiss()

    def _load_background_image_list(self):
        for i in range(len(self.background_image_list)):
            filename = "./adfi_client_app_data/background/" + str(i) + ".png"
            if os.path.exists(filename):
                self.background_image_list[i] = cv2.imread(filename)

    def load_settings(self, load_filename):
        ret_flg = False
        if load_filename is None:
            toast(self.app.textini[self.app.lang]["pp_toast_no_checkbox_message"])
            return ret_flg
        if self.app.camera_num is not None:
            load_dir = "./adfi_client_app_data/preprocessing_data"
            file_path = load_dir + "/" + load_filename + ".pkl"
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    pp_dict = pickle.load(f)
                self.ids["gray"].active = pp_dict["GRAY"]
                self.ids["blur_k_off"].state = "normal"
                self.ids["blur_k_1"].state = "normal"
                self.ids["blur_k_2"].state = "normal"
                self.ids["blur_k_3"].state = "normal"
                self.ids["blur_k_4"].state = "normal"
                if pp_dict["BLUR_KSIZE"] == 1:
                    self.ids["blur_k_1"].state = "down"
                if pp_dict["BLUR_KSIZE"] == 3:
                    self.ids["blur_k_2"].state = "down"
                if pp_dict["BLUR_KSIZE"] == 5:
                    self.ids["blur_k_3"].state = "down"
                if pp_dict["BLUR_KSIZE"] == 7:
                    self.ids["blur_k_4"].state = "down"

                self.ids["bg_sub"].active = pp_dict["BG_SUBTRACTION"]
                self.ids["bg_sub_th"].value = pp_dict["BG_SUBTRACTION_TH"]
                self.ids["bg_sub_mask"].active = pp_dict["BG_SUBTRACTION_MASK"]
                self.ids["invert"].active = pp_dict["INVERT"]
                self.ids["whitening"].value = pp_dict["WHITENING"]
                self.ids["blacking"].value = pp_dict["BLACKING"]
                self.ids["edge_k_off"].state = "normal"
                self.ids["edge_k_1"].state = "normal"
                self.ids["edge_k_2"].state = "normal"
                self.ids["edge_k_3"].state = "normal"
                self.ids["edge_k_4"].state = "normal"
                if pp_dict["EDGE_KSIZE"] == 1:
                    self.ids["edge_k_1"].state = "down"
                if pp_dict["EDGE_KSIZE"] == 3:
                    self.ids["edge_k_2"].state = "down"
                if pp_dict["EDGE_KSIZE"] == 5:
                    self.ids["edge_k_3"].state = "down"
                if pp_dict["EDGE_KSIZE"] == 7:
                    self.ids["edge_k_4"].state = "down"

                self.ids["binarization"].active = pp_dict["BINARIZATION"]
                self.ids["binarization_th"].value = pp_dict["BINARIZATION_TH"]
                self.ids["real_time_diff_off"].state = "normal"
                self.ids["real_time_diff_1"].state = "normal"
                self.ids["real_time_diff_2"].state = "normal"
                self.ids["real_time_diff_3"].state = "normal"
                self.ids["real_time_diff_4"].state = "normal"
                if pp_dict["REAL_TIME_DIFF_KSIZE"] == 1:
                    self.ids["real_time_diff_1"].state = "down"
                if pp_dict["REAL_TIME_DIFF_KSIZE"] == 3:
                    self.ids["real_time_diff_2"].state = "down"
                if pp_dict["REAL_TIME_DIFF_KSIZE"] == 5:
                    self.ids["real_time_diff_3"].state = "down"
                if pp_dict["REAL_TIME_DIFF_KSIZE"] == 7:
                    self.ids["real_time_diff_4"].state = "down"
                bg_image_path = load_dir + "/" + load_filename + ".png"
                if os.path.exists(bg_image_path):
                    self.show_save_background_popup(cv2.imread(bg_image_path))
                ret_flg = True
                toast(self.app.textini[self.app.lang]["pp_toast_load_message"])
        if not ret_flg:
            toast(self.app.textini[self.app.lang]["pp_toast_ng_load_message"])
        self.load_settings_popup_close()
        return ret_flg

    def get_processing_values(self):
        if self.ids["binarization"].active:
            self.ids["real_time_diff_off"].disabled = False
            self.ids["real_time_diff_1"].disabled = False
            self.ids["real_time_diff_2"].disabled = False
            self.ids["real_time_diff_3"].disabled = False
            self.ids["real_time_diff_4"].disabled = False
        else:
            self.ids["real_time_diff_off"].state = "down"
            self.ids["real_time_diff_1"].state = "normal"
            self.ids["real_time_diff_2"].state = "normal"
            self.ids["real_time_diff_3"].state = "normal"
            self.ids["real_time_diff_4"].state = "normal"
            self.ids["real_time_diff_off"].disabled = True
            self.ids["real_time_diff_1"].disabled = True
            self.ids["real_time_diff_2"].disabled = True
            self.ids["real_time_diff_3"].disabled = True
            self.ids["real_time_diff_4"].disabled = True

        self.gray = self.ids["gray"].active
        self.blur_method = "GAUSSIAN"
        if self.ids["blur_k_1"].state == "down":
            self.blur_ksize = 1
        elif self.ids["blur_k_2"].state == "down":
            self.blur_ksize = 3
        elif self.ids["blur_k_3"].state == "down":
            self.blur_ksize = 5
        elif self.ids["blur_k_4"].state == "down":
            self.blur_ksize = 7
        else:
            self.blur_ksize = None
            self.blur_method = None

        if self.background_image_list[self.app.camera_num] is not None:
            self.ids["bg_sub"].disabled = False
            self.ids["bg_sub_th"].disabled = False
        else:
            self.ids["bg_sub"].disabled = True
            self.ids["bg_sub_th"].disabled = True
            self.ids["bg_sub_mask"].disabled = True
        self.bg_sub = self.ids["bg_sub"].active
        self.bg_sub_th = self.ids["bg_sub_th"].value
        self.bg_sub_mask = self.ids["bg_sub_mask"].active
        if self.ids["bg_sub"].active:
            self.ids["bg_sub_mask"].disabled = False
        else:
            self.ids["bg_sub_mask"].disabled = True
        self.invert = self.ids["invert"].active

        self.whitening = self.ids["whitening"].value
        self.blacking = self.ids["blacking"].value

        self.edge_method = "LAPLACIAN"
        if self.ids["edge_k_1"].state == "down":
            self.edge_ksize = 1
        elif self.ids["edge_k_2"].state == "down":
            self.edge_ksize = 3
        elif self.ids["edge_k_3"].state == "down":
            self.edge_ksize = 5
        elif self.ids["edge_k_4"].state == "down":
            self.edge_ksize = 7
        else:
            self.edge_ksize = None
            self.edge_method = None

        self.binarization = self.ids["binarization"].active
        self.binarization_th = self.ids["binarization_th"].value

        self.real_time_diff = self.ids["binarization"].active
        if self.ids["real_time_diff_1"].state == "down":
            self.real_time_diff_ksize = 1
        elif self.ids["real_time_diff_2"].state == "down":
            self.real_time_diff_ksize = 3
        elif self.ids["real_time_diff_3"].state == "down":
            self.real_time_diff_ksize = 5
        elif self.ids["real_time_diff_4"].state == "down":
            self.real_time_diff_ksize = 7
        else:
            self.real_time_diff_ksize = None
            self.real_time_diff = None

        ret_dict = {
            "GRAY": self.gray,
            "BLUR_METHOD": self.blur_method,
            "BLUR_KSIZE": self.blur_ksize,
            "BG_SUBTRACTION": self.bg_sub,
            "BG_SUBTRACTION_TH": self.bg_sub_th,
            "BG_SUBTRACTION_MASK": self.bg_sub_mask,
            "INVERT": self.invert,
            "WHITENING": self.whitening,
            "BLACKING": self.blacking,
            "EDGE_METHOD": self.edge_method,
            "EDGE_KSIZE": self.edge_ksize,
            "BINARIZATION": self.binarization,
            "BINARIZATION_TH": self.binarization_th,
            "REAL_TIME_DIFF": self.real_time_diff,
            "REAL_TIME_DIFF_KSIZE": self.real_time_diff_ksize,
        }
        return ret_dict

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
        self.ids["applied_view"].on_pre_enter()

    def get_background_image(self):
        if (
            self.app.camera_num is not None
            and self.ids["applied_view"].frame is not None
        ):
            if self.background_image_list[self.app.camera_num] is None:
                self.background_image_list[self.app.camera_num] = self.ids[
                    "applied_view"
                ].full_frame
                save_dir = "./adfi_client_app_data/background"
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                cv2.imwrite(
                    save_dir + "/" + str(self.app.camera_num) + ".png",
                    self.background_image_list[self.app.camera_num],
                )
                toast(self.app.textini[self.app.lang]["pp_save_background_message"])
            else:
                self.show_save_background_popup(self.ids["applied_view"].full_frame)
        else:
            toast(self.app.textini[self.app.lang]["pp_ng_save_background_message"])

    def show_save_background_popup(self, tmp_background):
        self.tmp_background = tmp_background
        self.save_background_popup = Popup(
            title=self.app.textini[self.app.lang]["adfi_app_name"],
            content=DispBackgroundImages(
                popup_close=self.popup_close,
                save_background_image=self.save_background_image,
            ),
            size_hint=(0.6, 0.6),
        )
        self.save_background_popup.open()

    def popup_close(self):
        self.save_background_popup.dismiss()

    def save_background_image(self):
        if self.app.camera_num is not None:
            if self.tmp_background is not None:
                self.background_image_list[self.app.camera_num] = self.tmp_background
                save_dir = "./adfi_client_app_data/background"
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                cv2.imwrite(
                    save_dir + "/" + str(self.app.camera_num) + ".png",
                    self.background_image_list[self.app.camera_num],
                )
                toast(self.app.textini[self.app.lang]["pp_save_background_message"])
            else:
                toast(self.app.textini[self.app.lang]["pp_ng_save_background_message"])
            self.save_background_popup.dismiss()

    def save_settings(self, save_name):
        if self._validate_name(save_name):
            if self.app.camera_num is not None:
                pp_dict = self.get_processing_values()
                save_dir = "./adfi_client_app_data/preprocessing_data"
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                dt_now = datetime.datetime.now()
                create_time = dt_now.strftime("%Y/%m/%d %H:%M:%S")
                save_filename = dt_now.strftime("%Y%m%d%H%M%S")
                bg_image = False
                if self.background_image_list[self.app.camera_num] is not None:
                    cv2.imwrite(
                        save_dir + "/" + save_filename + ".png",
                        self.background_image_list[self.app.camera_num],
                    )
                    bg_image = True
                pp_dict.update(
                    {
                        "NAME": save_name,
                        "FILENAME": save_filename,
                        "BG_IMAGE": bg_image,
                        "CREATE_TIME": create_time,
                        "UPDATE_TIME": create_time,
                        "CAMERA_NUM": self.app.camera_num,
                    }
                )
                with open(save_dir + "/" + save_filename + ".pkl", "wb") as f:
                    pickle.dump(pp_dict, f)
                toast(self.app.textini[self.app.lang]["pp_toast_save_message"])
            else:
                toast(self.app.textini[self.app.lang]["pp_toast_ng_save_message"])
            self.save_settings_popup_close()

    def _validate_name(self, name):
        re_compile = re.compile(r"^[a-zA-Z0-9_-]+$")
        flg = True
        if len(name) == 0:
            flg = False
            toast(self.app.textini[self.app.lang]["pp_toast_error_message_no_name"])
        elif len(name) > 30:
            flg = False
            toast(self.app.textini[self.app.lang]["pp_toast_error_message_max_len"])
        elif re_compile.match(name) is None:
            flg = False
            toast(self.app.textini[self.app.lang]["pp_toast_error_message_ascii"])
        return flg

    def save_settings_popup_close(self):
        self.save_settings_popup.dismiss()

    def show_save_settings_popup(self):

        target_dir = "./adfi_client_app_data/preprocessing_data"
        path_list = glob.glob(target_dir + "/*.pkl")
        if len(path_list) > 9:
            toast(
                self.app.textini[self.app.lang][
                    "pp_toast_error_message_max_settings_num"
                ]
            )
        else:
            self.save_settings_popup = Popup(
                title=self.app.textini[self.app.lang]["adfi_app_name"],
                content=SaveSettingsContent(
                    popup_close=self.save_settings_popup_close,
                    save_settings=self.save_settings,
                ),
                size_hint=(0.3, 0.25),
            )
            self.save_settings_popup.open()

    def load_settings_popup_close(self):
        self.load_settings_popup.dismiss()

    def show_load_settings_popup(self):
        self.load_settings_popup = Popup(
            title=self.app.textini[self.app.lang]["adfi_app_name"],
            content=LoadSettingsContent(
                popup_close=self.load_settings_popup_close,
                load_settings=self.load_settings,
            ),
            size_hint=(0.6, 0.9),
        )
        self.load_settings_popup.open()


class LoadSettingsContent(MDBoxLayout):
    popup_close = ObjectProperty(None)
    load_settings = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LoadSettingsContent, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.screen = self.app.sm.get_screen("preprocessing")
        self.settings_list = []
        self.disp_settings_list()

    def get_filename(self):
        ret = None
        for i in range(len(self.settings_list)):
            id_box = "checkbox_" + str(i)
            if self.ids[id_box].active:
                ret = self.settings_list[i]["FILENAME"]
        return ret

    def get_name(self):
        ret = None
        for i in range(len(self.settings_list)):
            id_box = "checkbox_" + str(i)
            if self.ids[id_box].active:
                ret = self.settings_list[i]["NAME"]
        return ret

    def disp_settings_list(self):
        target_dir = "./adfi_client_app_data/preprocessing_data"
        path_list = glob.glob(target_dir + "/*.pkl")
        if len(path_list) > 0:
            count = 0
            for path in path_list:
                with open(path, "rb") as f:
                    settings_dict = pickle.load(f)
                self.settings_list.append(settings_dict)
                self.ids["checkbox_" + str(count)].disabled = False
                self.ids["name_" + str(count)].text = str(settings_dict["NAME"])
                self.ids["camera_num_" + str(count)].text = str(
                    settings_dict["CAMERA_NUM"]
                )
                self.ids["creat_time_" + str(count)].text = str(
                    settings_dict["CREATE_TIME"]
                )
                count += 1
                if count > 9:
                    break
        else:
            self.ids["name_0"].text = "No Data"


class SaveSettingsContent(MDBoxLayout):
    popup_close = ObjectProperty(None)
    save_settings = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SaveSettingsContent, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.screen = self.app.sm.get_screen("preprocessing")


class DispBackgroundImages(MDBoxLayout):
    popup_close = ObjectProperty(None)
    save_background_image = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(DispBackgroundImages, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.screen = self.app.sm.get_screen("preprocessing")
        self.image_view = self.screen.ids["image_view"]

        old_background = self.screen.background_image_list[self.app.camera_num]
        new_background = self.screen.tmp_background

        if old_background is not None:
            old_background = self.app.resize_cv_image(
                self.app.crop_image_ratio(
                    old_background,
                    self.image_view.ratio1,
                    self.image_view.ratio2,
                ),
                size_max=self.image_view.image_size,
            )
            flip_old = cv2.flip(old_background, 0)
            if flip_old is not None:
                buf = flip_old.tobytes()
                old_texture = Texture.create(
                    size=(old_background.shape[1], old_background.shape[0]),
                    colorfmt="bgr",
                )
                old_texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
                self.ids["old_background"].texture = old_texture
                self.ids["old_background"].size = old_texture.size

        if new_background is not None:
            new_background = self.app.resize_cv_image(
                self.app.crop_image_ratio(
                    new_background,
                    self.image_view.ratio1,
                    self.image_view.ratio2,
                ),
                size_max=self.image_view.image_size,
            )
            flip_new = cv2.flip(new_background, 0)
            if flip_new is not None:
                buf = flip_new.tobytes()
                new_texture = Texture.create(
                    size=(new_background.shape[1], new_background.shape[0]),
                    colorfmt="bgr",
                )
                new_texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
                self.ids["new_background"].texture = new_texture
                self.ids["new_background"].size = new_texture.size


class AppliedImageView(MDFloatLayout):
    def __init__(self, **kwargs):
        super(AppliedImageView, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.pos = (550, 220)
        self.image_size = (500, 500)
        self.full_frame = None
        self.frame = None
        self.tmp_texture = None
        self.image_processing = ImageProcessing()

    def on_pre_enter(self):
        self.screen = self.app.sm.get_screen("preprocessing")
        self.image_view = self.screen.ids["image_view"]
        Clock.schedule_interval(self._disp_canvas, 1.0 / float(self.app.confini["settings"]["display_fps"]))

    def _get_image(self):
        if len(self.image_view.frame_list) > 0:
            self.full_frame = self.image_processing.multi_frame_smoothing(
                self.image_view.frame_list
            )
            self.frame = self.app.resize_cv_image(
                self.app.crop_image_ratio(
                    self.full_frame,
                    self.image_view.ratio1,
                    self.image_view.ratio2,
                ),
                size_max=self.image_view.image_size,
            )

            p_values = self.screen.get_processing_values()
            crop_bg = None
            if self.screen.background_image_list[self.app.camera_num] is not None:
                crop_bg = self.app.resize_cv_image(
                    self.app.crop_image_ratio(
                        self.screen.background_image_list[self.app.camera_num],
                        self.image_view.ratio1,
                        self.image_view.ratio2,
                    ),
                    size_max=self.image_view.image_size,
                )
            tmp_frame = self.image_processing.do_image_processing(
                self.frame,
                p_values,
                bg_image=crop_bg,
            )
            flip_frame = cv2.flip(tmp_frame, 0)
            if flip_frame is not None:
                buf = flip_frame.tobytes()
                texture = Texture.create(
                    size=(tmp_frame.shape[1], tmp_frame.shape[0]),
                    colorfmt="bgr",
                )
                texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
                self.tmp_texture = texture

    def _disp_canvas(self, dt):
        self._get_image()
        if self.tmp_texture is not None:
            self.canvas.before.clear()
            self.canvas.before.add(Color(rgb=[1, 1, 1]))
            self.canvas.before.add(
                Rectangle(
                    texture=self.tmp_texture, pos=self.pos, size=self.tmp_texture.size
                )
            )


class PreprocessingImageView(MDFloatLayout):
    def __init__(self, **kwargs):
        super(PreprocessingImageView, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.active_flg = False
        self.frame = None
        self.frame_list = []
        self.frame_list_max = 5
        self.cap = None
        self.tmp_texture = None
        self.screen = None
        self.pos = (50, 220)
        self.image_size = (500, 500)
        self.ratio1 = None
        self.ratio2 = None

    def active_camera(self, camera_num):
        self.active_flg = self.app.camera_parameter_list[camera_num]["ACTIVE"]
        self.screen = self.app.sm.get_screen("preprocessing")
        if self.cap is not None or not self.active_flg:
            self.clock_unschedule()
        if self.active_flg:
            self.cap = self.app.camera_list[camera_num]
            self.app.camera_num = camera_num
            self.ratio1 = None
            self.ratio2 = None
            self.frame_list = []
            self.screen.ids["camera_name"].text = "Camera " + str(camera_num)
            self.load_camera_parameter()
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
            if tmp_frame is not None:
                self.frame_list.append(tmp_frame)
                if len(self.frame_list) > self.frame_list_max:
                    del self.frame_list[0]
                self.frame = self.app.resize_cv_image(
                    self.app.crop_image_ratio(tmp_frame, self.ratio1, self.ratio2),
                    size_max=self.image_size,
                )

                flip_frame = cv2.flip(self.frame, 0)
                if flip_frame is not None:
                    buf = flip_frame.tobytes()
                    texture = Texture.create(
                        size=(self.frame.shape[1], self.frame.shape[0]),
                        colorfmt="bgr",
                    )
                    texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
                    self.tmp_texture = texture

    def _disp_canvas(self, dt):
        if self.tmp_texture is not None:
            self.canvas.before.clear()
            self.canvas.before.add(Color(rgb=[1, 1, 1]))
            self.canvas.before.add(
                Rectangle(
                    texture=self.tmp_texture, pos=self.pos, size=self.tmp_texture.size
                )
            )
