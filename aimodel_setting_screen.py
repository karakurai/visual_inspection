import datetime
import glob
import os
import pickle
import re
import shutil

from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen


class AimodelSettingScreen(MDScreen):
    def __init__(self, **kwargs):
        super(AimodelSettingScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.save_aimodel_popup = None
        self.settings_list = []
        self.inspection_dict = None
        self.pickle_path = None

    def on_pre_enter(self):
        self.clear_text()
        self.disp_aimodel_list()

    def get_current_inspection_dict(self):
        inspections_dict = None
        target_dir = "./adfi_client_app_data/current_inspection"
        path_list = glob.glob(target_dir + "/*.pkl")
        if len(path_list) > 0:
            self.pickle_path = path_list[0]
            with open(self.pickle_path, "rb") as f:
                inspections_dict = pickle.load(f)
        return inspections_dict

    def disp_aimodel_list(self):
        self.ids["name_0"].text = "No Data"
        self.inspection_dict = self.get_current_inspection_dict()
        if self.inspection_dict is not None:
            self.settings_list = self.inspection_dict["PREPROCESSING_LIST"]
            if len(self.settings_list) > 0:
                for count in range(len(self.settings_list)):
                    settings_dict = self.settings_list[count]
                    self.ids["checkbox_" + str(count)].disabled = False
                    self.ids["name_" + str(count)].text = str(settings_dict["NAME"])
                    self.ids["camera_num_" + str(count)].text = str(
                        settings_dict["CAMERA_NUM"]
                    )
                    if "API_KEY" in settings_dict:
                        self.ids["api_key_" + str(count)].text = str(
                            settings_dict["API_KEY"]
                        )
                    else:
                        self.ids["api_key_" + str(count)].text = ""
                    if "MODEL_ID" in settings_dict:
                        self.ids["model_id_" + str(count)].text = str(
                            settings_dict["MODEL_ID"]
                        )
                    else:
                        self.ids["model_id_" + str(count)].text = ""
                    if "MODEL_TYPE" in settings_dict:
                        self.ids["model_type_" + str(count)].text = str(
                            settings_dict["MODEL_TYPE"]
                        )
                    else:
                        self.ids["model_type_" + str(count)].text = ""
                    count += 1
                    if count > 9:
                        break

    def clear_text(self):
        for i in range(10):
            self.ids["checkbox_" + str(i)].active = False
            self.ids["checkbox_" + str(i)].disabled = True
            self.ids["name_" + str(i)].text = ""
            self.ids["camera_num_" + str(i)].text = ""
            self.ids["api_key_" + str(i)].text = ""
            self.ids["model_id_" + str(i)].text = ""
            self.ids["model_type_" + str(i)].text = ""

    def get_checkbox_num(self):
        for i in range(10):
            if self.ids["checkbox_" + str(i)].active:
                return i
        return -1

    def show_save_aimodel_popup(self):
        checkbox_num = self.get_checkbox_num()
        if checkbox_num < 0:
            toast(self.app.textini[self.app.lang]["as_toast_message_no_check"])
        else:
            self.save_aimodel_popup = Popup(
                title=self.app.textini[self.app.lang]["adfi_app_name"],
                content=SaveAimodelContent(
                    popup_close=self.save_aimodel_popup_close,
                    save_aimodel=self.save_aimodel,
                ),
                size_hint=(0.4, 0.4),
            )
            self.save_aimodel_popup.open()

    def save_aimodel_popup_close(self):
        self.save_aimodel_popup.dismiss()

    def save_aimodel(self, api_key, model_id, model_type):
        checkbox_num = self.get_checkbox_num()
        if checkbox_num < 0:
            toast(self.app.textini[self.app.lang]["as_toast_message_no_check"])
        else:
            if self._validate_aimodel(api_key, model_id, model_type):
                setting_dict = self.settings_list[int(checkbox_num)]
                setting_dict.update(
                    {"API_KEY": api_key, "MODEL_ID": model_id, "MODEL_TYPE": model_type}
                )
                self.settings_list[int(checkbox_num)] = setting_dict
                self.inspection_dict["PREPROCESSING_LIST"] = self.settings_list
                if self.pickle_path is not None:
                    with open(self.pickle_path, "wb") as f:
                        pickle.dump(self.inspection_dict, f)
                    to_dir = "./adfi_client_app_data/inspection_data"
                    shutil.copy2(self.pickle_path, to_dir)
                    toast(self.app.textini[self.app.lang]["as_toast_message_save"])
                self.disp_aimodel_list()
                self.save_aimodel_popup_close()

    def _validate_aimodel(self, api_key, model_id, model_type):
        re_compile = re.compile(r"^[a-zA-Z0-9_-]+$")
        flg = True
        if len(api_key) > 40:
            flg = False
            toast(self.app.textini[self.app.lang]["as_toast_error_message_max_len_key"])
        elif len(api_key) > 0 and re_compile.match(api_key) is None:
            flg = False
            toast(self.app.textini[self.app.lang]["as_toast_error_message_ascii_key"])
        if len(model_id) > 40:
            flg = False
            toast(self.app.textini[self.app.lang]["as_toast_error_message_max_len_id"])
        elif len(model_id) > 0 and re_compile.match(model_id) is None:
            flg = False
            toast(self.app.textini[self.app.lang]["as_toast_error_message_ascii_id"])
        if len(model_type) > 3:
            flg = False
            toast(
                self.app.textini[self.app.lang]["as_toast_error_message_max_len_type"]
            )
        elif len(model_type) > 0 and re_compile.match(model_type) is None:
            flg = False
            toast(self.app.textini[self.app.lang]["as_toast_error_message_ascii_type"])
        return flg


class SaveAimodelContent(MDBoxLayout):
    popup_close = ObjectProperty(None)
    save_aimodel = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SaveAimodelContent, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.screen = self.app.sm.get_screen("aimodel_setting")
        self.check_num = self.screen.get_checkbox_num()
        self.ids["api_key"].text = self.screen.ids[
            "api_key_" + str(self.check_num)
        ].text
        self.ids["model_id"].text = self.screen.ids[
            "model_id_" + str(self.check_num)
        ].text
        self.ids["model_type"].text = self.screen.ids[
            "model_type_" + str(self.check_num)
        ].text
