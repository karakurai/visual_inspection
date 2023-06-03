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


class InspectionSettingScreen(MDScreen):
    def __init__(self, **kwargs):
        super(InspectionSettingScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.save_inspection_popup = None
        self.preprocessing_popup = None
        self.details_popup = None
        self.new_inspection_name = ""
        self.delete_inspection_dialog = None
        self.inspection_list = []

    def on_pre_enter(self):
        self.new_inspection_name = ""
        self.disp_inspections_list()

    def get_current_inspection_filename(self):
        filename = ""
        target_dir = "./adfi_client_app_data/current_inspection"
        path_list = glob.glob(target_dir + "/*.pkl")
        if len(path_list) > 0:
            with open(path_list[0], "rb") as f:
                inspections_dict = pickle.load(f)
            filename = inspections_dict["FILENAME"]
        return filename

    def stop_inspection(self):
        current_dir = "./adfi_client_app_data/current_inspection"
        path_list = glob.glob(current_dir + "/*")
        if len(path_list) > 0:
            for f in path_list:
                os.remove(f)
            self.app.current_inspection_dict = None
            toast(self.app.textini[self.app.lang]["is_toast_stop_inspection_message"])
            self.disp_inspections_list()
        else:
            toast(
                self.app.textini[self.app.lang]["is_toast_stop_inspection_ng_message"]
            )

    def run_inspection(self, filename):
        if filename is not None:
            from_dir = "./adfi_client_app_data/inspection_data"
            to_dir = "./adfi_client_app_data/current_inspection"
            file_path = from_dir + "/" + filename + ".pkl"
            if not os.path.exists(to_dir):
                os.makedirs(to_dir)
            if os.path.exists(file_path):
                path_list = glob.glob(to_dir + "/*")
                if len(path_list) > 0:
                    for f in path_list:
                        os.remove(f)
                shutil.copy2(file_path, to_dir)
                with open(file_path, "rb") as f:
                    inspection_dict = pickle.load(f)
                for pre_dict in inspection_dict["PREPROCESSING_LIST"]:
                    pre_filename = pre_dict["FILENAME"]
                    image_path = from_dir + "/" + filename + "_" + pre_filename + ".png"
                    if os.path.exists(image_path):
                        shutil.copy2(
                            image_path,
                            to_dir + "/" + filename + "_" + pre_filename + ".png",
                        )
                toast(
                    self.app.textini[self.app.lang]["is_toast_run_inspection_message"]
                )
                self.disp_inspections_list()
        else:
            toast(self.app.textini[self.app.lang]["is_toast_run_inspection_ng_message"])

    def disp_inspections_list(self):
        current_inspection_filename = self.get_current_inspection_filename()
        self.inspection_list = []
        self.ids["stop_button"].disabled = True
        self.ids["run_button"].disabled = True
        for i in range(10):
            self.ids["checkbox_" + str(i)].disabled = True
            self.ids["name_" + str(i)].text = ""
            self.ids["preprocessing_num_" + str(i)].text = ""
            self.ids["creat_time_" + str(i)].text = ""
        self.preprocessing_filename_dict = {}
        target_dir = "./adfi_client_app_data/inspection_data"
        path_list = glob.glob(target_dir + "/*.pkl")
        if len(path_list) > 0:
            count = 0
            for path in path_list:
                with open(path, "rb") as f:
                    inspections_dict = pickle.load(f)
                self.inspection_list.append(inspections_dict)
                self.ids["checkbox_" + str(count)].disabled = False
                if current_inspection_filename == inspections_dict["FILENAME"]:
                    self.ids["name_" + str(count)].text = (
                        self.app.textini[self.app.lang]["running"]
                        + "  "
                        + str(inspections_dict["NAME"])
                    )
                    self.ids["stop_button"].disabled = False
                else:
                    self.ids["name_" + str(count)].text = str(inspections_dict["NAME"])
                    self.ids["run_button"].disabled = False
                self.ids["preprocessing_num_" + str(count)].text = str(
                    len(inspections_dict["PREPROCESSING_LIST"])
                )
                self.ids["creat_time_" + str(count)].text = str(
                    inspections_dict["CREATE_TIME"]
                )
                self.preprocessing_filename_dict.update(
                    {"checkbox_" + str(count): inspections_dict["FILENAME"]}
                )
                count += 1
                if count > 9:
                    break
            self.ids["details_button"].disabled = False
            self.ids["delete_button"].disabled = False
        else:
            self.ids["name_0"].text = "No Data"
            self.ids["details_button"].disabled = True
            self.ids["delete_button"].disabled = True

    def get_filename(self):
        ret = None
        for i in range(len(self.inspection_list)):
            id_box = "checkbox_" + str(i)
            if self.ids[id_box].active:
                ret = self.inspection_list[i]["FILENAME"]
        return ret

    def get_name(self):
        ret = None
        for i in range(len(self.inspection_list)):
            id_box = "checkbox_" + str(i)
            if self.ids[id_box].active:
                ret = self.inspection_list[i]["NAME"]
        return ret

    def show_delete_inspection_dialog(self, delete_filename, delete_name):
        if delete_filename is None or delete_name is None:
            toast(self.app.textini[self.app.lang]["is_toast_no_checkbox_message"])
        elif delete_filename == self.get_current_inspection_filename():
            toast(
                self.app.textini[self.app.lang]["is_toast_current_inspection_message"]
            )
        else:
            self.delete_inspection_dialog = MDDialog(
                text=self.app.textini[self.app.lang]["is_dialog_delete_message"]
                + "\n\n"
                + self.app.textini[self.app.lang]["name"]
                + ": "
                + delete_name,
                buttons=[
                    MDFlatButton(
                        text=self.app.textini[self.app.lang]["cansel"],
                        text_color=self.app.theme_cls.primary_color,
                        on_release=lambda x: self.delete_inspection_dialog.dismiss(),
                    ),
                    MDFlatButton(
                        text=self.app.textini[self.app.lang]["delete"],
                        text_color=self.app.theme_cls.primary_color,
                        on_release=lambda x: self.delete_inspection(delete_filename),
                    ),
                ],
            )
            self.delete_inspection_dialog.open()

    def delete_inspection(self, delete_filename):
        if delete_filename == self.get_current_inspection_filename():
            toast(self.app.textini[self.app.lang]["is_toast_delete_ng_message"])
        else:
            delete_dir = "./adfi_client_app_data/inspection_data"
            file_path = delete_dir + "/" + delete_filename + ".pkl"
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    inspection_dict = pickle.load(f)
                for pre_dict in inspection_dict["PREPROCESSING_LIST"]:
                    pre_filename = pre_dict["FILENAME"]
                    image_path = (
                        delete_dir + "/" + delete_filename + "_" + pre_filename + ".png"
                    )
                    if os.path.exists(image_path):
                        os.remove(image_path)
                os.remove(file_path)

            toast(self.app.textini[self.app.lang]["is_toast_delete_message"])
            self.disp_inspections_list()
        self.delete_inspection_dialog.dismiss()

    def show_save_settings_popup(self):
        preprocessing_dir = "./adfi_client_app_data/preprocessing_data"
        preprocessing_list = glob.glob(preprocessing_dir + "/*.pkl")
        if len(preprocessing_list) == 0:
            toast(self.app.textini[self.app.lang]["is_toast_no_preprocessing_message"])
        else:
            target_dir = "./adfi_client_app_data/inspection_data"
            path_list = glob.glob(target_dir + "/*.pkl")
            if len(path_list) > 9:
                toast(
                    self.app.textini[self.app.lang][
                        "is_toast_error_message_max_inspection_num"
                    ]
                )
            else:
                self.save_inspection_popup = Popup(
                    title=self.app.textini[self.app.lang]["adfi_app_name"],
                    content=SaveInspectionContent(
                        popup_close=self.save_inspection_popup_close,
                        save_inspection=self.save_inspection,
                    ),
                    size_hint=(0.3, 0.25),
                )
                self.save_inspection_popup.open()

    def save_inspection_popup_close(self):
        self.save_inspection_popup.dismiss()

    def save_inspection(self, save_name):
        if self._validate_name(save_name):
            self.new_inspection_name = save_name
            self.save_inspection_popup_close()
            self.show_preprocessing_popup()

    def _validate_name(self, name):
        re_compile = re.compile(r"^[a-zA-Z0-9_-]+$")
        flg = True
        if len(name) == 0:
            flg = False
            toast(self.app.textini[self.app.lang]["is_toast_error_message_no_name"])
        elif len(name) > 30:
            flg = False
            toast(self.app.textini[self.app.lang]["is_toast_error_message_max_len"])
        elif re_compile.match(name) is None:
            flg = False
            toast(self.app.textini[self.app.lang]["is_toast_error_message_ascii"])
        return flg

    def show_preprocessing_popup(self):
        self.preprocessing_popup = Popup(
            title=self.app.textini[self.app.lang]["adfi_app_name"],
            content=PreprocessingListContent(
                popup_close=self.preprocessing_popup_close,
                create_inspection=self.create_inspection,
            ),
            size_hint=(0.6, 0.9),
        )
        self.preprocessing_popup.open()

    def preprocessing_popup_close(self):
        self.preprocessing_popup.dismiss()

    def show_details_popup(self, filename, inspection_name):
        if filename is None or inspection_name is None:
            toast(self.app.textini[self.app.lang]["is_toast_no_checkbox_message"])
        else:
            self.details_popup = Popup(
                title=self.app.textini[self.app.lang]["adfi_app_name"],
                content=DetailsContent(
                    popup_close=self.details_popup_close,
                    inspection_name=inspection_name,
                    filename=filename,
                ),
                size_hint=(0.6, 0.9),
            )
            self.details_popup.open()

    def details_popup_close(self):
        self.details_popup.dismiss()

    def create_inspection(self, preprocessing_filename_list):
        dt_now = datetime.datetime.now()
        create_time = dt_now.strftime("%Y/%m/%d %H:%M:%S")
        save_filename = dt_now.strftime("%Y%m%d%H%M%S")
        save_dir = "./adfi_client_app_data/inspection_data"
        current_inspection_dir = "./adfi_client_app_data/current_inspection"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        if not os.path.exists(current_inspection_dir):
            os.makedirs(current_inspection_dir)
        inspection_count = len(glob.glob(save_dir + "/*.pkl"))

        inspection_dict = {
            "NAME": self.new_inspection_name,
            "CREATE_TIME": create_time,
            "FILENAME": save_filename,
            "PREPROCESSING_LIST": [],
        }
        preprocessing_dir = "./adfi_client_app_data/preprocessing_data"
        preprocessing_list = glob.glob(preprocessing_dir + "/*.pkl")
        if len(preprocessing_list) > 0:
            for path in preprocessing_list:
                with open(path, "rb") as f:
                    preprocessing_dict = pickle.load(f)
                if preprocessing_dict["FILENAME"] in preprocessing_filename_list:
                    inspection_dict["PREPROCESSING_LIST"].append(preprocessing_dict)
                    imagefile_path = (
                        preprocessing_dir
                        + "/"
                        + preprocessing_dict["FILENAME"]
                        + ".png"
                    )
                    if os.path.exists(imagefile_path):
                        shutil.copy2(
                            imagefile_path,
                            save_dir
                            + "/"
                            + save_filename
                            + "_"
                            + preprocessing_dict["FILENAME"]
                            + ".png",
                        )
                        if inspection_count == 0:
                            shutil.copy2(
                                imagefile_path,
                                current_inspection_dir
                                + "/"
                                + save_filename
                                + "_"
                                + preprocessing_dict["FILENAME"]
                                + ".png",
                            )
            with open(save_dir + "/" + save_filename + ".pkl", "wb") as f:
                pickle.dump(inspection_dict, f)
            if inspection_count == 0:
                with open(
                    current_inspection_dir + "/" + save_filename + ".pkl", "wb"
                ) as f:
                    pickle.dump(inspection_dict, f)

            toast(self.app.textini[self.app.lang]["is_toast_create_message"])
            self.disp_inspections_list()
        else:
            toast(self.app.textini[self.app.lang]["is_toast_no_preprocessing_message"])
        self.preprocessing_popup_close()


class SaveInspectionContent(MDBoxLayout):
    popup_close = ObjectProperty(None)
    save_inspection = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SaveInspectionContent, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.screen = self.app.sm.get_screen("inspection_setting")


class PreprocessingListContent(MDBoxLayout):
    popup_close = ObjectProperty(None)
    create_inspection = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PreprocessingListContent, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.screen = self.app.sm.get_screen("inspection_setting")
        self.new_inspection_name = self.screen.new_inspection_name
        self.ids["new_inspection_name"].text = (
            self.app.textini[self.app.lang]["inspection_name"]
            + ": "
            + str(self.new_inspection_name)
        )
        self.preprocessing_filename_dict = {}
        self.disp_settings_list()

    def disp_settings_list(self):
        self.preprocessing_filename_dict = {}
        target_dir = "./adfi_client_app_data/preprocessing_data"
        path_list = glob.glob(target_dir + "/*.pkl")
        if len(path_list) > 0:
            count = 0
            for path in path_list:
                with open(path, "rb") as f:
                    settings_dict = pickle.load(f)
                self.ids["checkbox_" + str(count)].disabled = False
                self.ids["name_" + str(count)].text = str(settings_dict["NAME"])
                self.ids["camera_num_" + str(count)].text = str(
                    settings_dict["CAMERA_NUM"]
                )
                self.ids["creat_time_" + str(count)].text = str(
                    settings_dict["CREATE_TIME"]
                )
                self.preprocessing_filename_dict.update(
                    {"checkbox_" + str(count): settings_dict["FILENAME"]}
                )
                count += 1
                if count > 9:
                    break
        else:
            self.ids["name_0"].text = "No Data"

    def craete_new_inspection(self):
        preprocessing_filename_list = []
        count = 0
        for i in range(10):
            index = "checkbox_" + str(i)
            if self.ids[index].active:
                preprocessing_filename_list.append(
                    self.preprocessing_filename_dict[index]
                )
                count += 1
        if count <= 5:
            self.create_inspection(preprocessing_filename_list)
        else:
            toast(
                self.app.textini[self.app.lang]["is_toast_many_preprocessing_message"]
            )


class DetailsContent(MDBoxLayout):
    popup_close = ObjectProperty(None)
    inspection_name = ObjectProperty(None)
    filename = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(DetailsContent, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.screen = self.app.sm.get_screen("inspection_setting")
        self.ids["inspection_name"].text = (
            self.app.textini[self.app.lang]["inspection_name"]
            + ": "
            + str(self.inspection_name)
        )
        self.preprocessing_filename_dict = {}
        self.disp_details(self.filename)

    def disp_details(self, filename):
        self.ids["name_0"].text = "No Data"
        target_dir = "./adfi_client_app_data/inspection_data"
        path = target_dir + "/" + filename + ".pkl"
        if os.path.exists(path):
            with open(path, "rb") as f:
                inspections_dict = pickle.load(f)

            settings_list = inspections_dict["PREPROCESSING_LIST"]
            if len(settings_list) > 0:
                count = 0
                for settings_dict in settings_list:
                    self.ids["checkbox_" + str(count)].disabled = True
                    self.ids["checkbox_" + str(count)].active = True
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
