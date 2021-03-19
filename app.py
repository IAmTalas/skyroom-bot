import os
import platform
import time
from datetime import datetime

import pytz
import requests
import schedule
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from tabulate import tabulate

from database import database


class App:
    def __init__(self) -> None:
        App.inputs()

    @staticmethod
    def inputs():

        App.clear_screen()
        while True:
            try:
                class_count = int(
                    input("How many classes do you want to attend : ".title())
                )
                break
            except ValueError:
                print("ERROR : please enter a number ")
        plan = []
        for session in range(class_count):

            while True:

                loop_stop = False
                while True:
                    try:
                        start_time = (
                            input("enter class beginning time : ")
                            .replace(" ", "")
                            .split(":")
                        )
                        if (0 <= int(start_time[0]) <= 23) and (
                            0 <= int(start_time[1]) <= 59
                        ):
                            break
                        else:
                            print(
                                "ERROR : time format is not correct please enter again"
                            )

                    except ValueError:
                        print("ERROR : values should be number and separated by : ")
                    except IndexError:
                        print("time format is not correct please enter again")

                while True:
                    end_time = (
                        input("enter class ending time : ").replace(" ", "").split(":")
                    )
                    try:
                        if (0 <= int(end_time[0]) <= 23) and (
                            0 <= int(end_time[1]) <= 59
                        ):
                            break
                        else:
                            print(
                                "ERROR : time format is not correct plase try agein! "
                            )
                    except IndexError:
                        print("time format is not correct please enter again")
                    except ValueError:
                        print("ERROR : values should be number and sprated by : ")

                if int(end_time[0]) > int(start_time[0]):
                    break
                else:
                    if int(end_time[0]) == int(start_time[0]) and int(
                        end_time[1]
                    ) > int(start_time[1]):
                        break
                    else:
                        print("ERROR : start time should be before than end time!")
                        continue
            while True:
                utc_status = input(
                    "do you want to convert the time zone to UTC [Y/N] : "
                )
                if utc_status.upper()[0] == "Y":
                    utc_status = True
                    break
                elif utc_status.upper()[0] == "N":
                    utc_status = False
                    break
                else:
                    print("ERROR : invalid input please try again.")

            App.clear_screen()

            start_time = f"{int(start_time[0]):02d}:{int(start_time[1]):02d}"
            end_time = f"{int(end_time[0]):02d}:{int(end_time[1]):02d}"

            database.make_connection()

            mode = 1

            while True:
                if mode == 2:
                    teacher_id = int(input("select your teachers id : "))
                    teachers_info = database.get_teachers_id(teacher_id)
                    print(teachers_info)
                    if len(teachers_info) == 1:
                        break
                        link = teachers_info[0][2]
                    else:
                        print(
                            "ERROR : there is no teacher with {} id ".format(teacher_id)
                        )
                if mode == 1:
                    try:
                        print(
                            "enter the link carefully if its wrong progeam will be crashed link must be like : https://example.com\nDONT FORGET TO PUT http:// "
                        )
                        link = input("please enter class url : ").strip()
                        status_code = requests.get(link).status_code
                        if int(status_code) == 200:
                            break
                    except:
                        print("ERROR : internet connetion or url had a problem")

            while True:
                login_mode = int(
                    input(
                        "1)as guess(don't require account) \n2)with your username and password\nselect the mode : "
                    )
                )
                if login_mode == 1 or login_mode == 2:
                    break
                else:
                    print("ERROR : please enter a vaild mode ")
            plan.append(
                {
                    "link": link,
                    "start_time": App.local_to_utc(start_time)
                    if utc_status
                    else start_time,
                    "end_time": App.local_to_utc(end_time) if utc_status else end_time,
                    "login_mode": "guess" if login_mode == 1 else "account",
                }
            )
        App.username_password(login_mode)
        App.scheduler(plan)

    def local_to_utc(time):
        local = pytz.timezone("asia/tehran")
        naive = datetime.strptime(f"2021-1-3 {time}:00", "%Y-%m-%d %H:%M:%S")
        local_dt = local.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        return f"{int(utc_dt.hour):02d}:{int(utc_dt.minute):02d}"

    @classmethod
    def username_password(cls, login_mode):

        if login_mode == "account":
            cls.username = input("enter your username : ")
            cls.password = input("enter your password : ")
        else:
            cls.username = input("enter your username : ")

    def clear_screen():

        if os.name == "nt":
            _ = os.system("cls")

        else:
            _ = os.system("clear")

    def send_massages():
        massages_list = []
        pass

    if platform.system().lower() == "linux":
        browser = webdriver.Firefox(executable_path=r"./driver/geckodriver")
    elif platform.system().lower() == "windows":
        browser = webdriver.Firefox(executable_path=r".\driver\geckodriver.exe")

    @staticmethod
    def run_service(username, password, link, login_mode):
        App.browser.get(link)
        time.sleep(5)
        App.login_into_class(username, password, link, login_mode)

    @staticmethod
    def stop_service():
        App.browser.get("about:blank")

    @staticmethod
    def kill_service():
        App.browser.close()

    @staticmethod
    def scheduler(data):

        for session in range(len(data)):
            schedule.every().day.at(data[session]["start_time"]).do(
                App.run_service,
                username=App.username,
                password=App.password
                if data[session]["login_mode"] == "account"
                else "",
                link=data[session]["link"],
                login_mode=data[session]["login_mode"],
            )
            if session == len(data) - 1:
                schedule.every().day.at(data[session]["end_time"]).do(App.kill_service)
            else:
                schedule.every().day.at(data[session]["end_time"]).do(App.stop_service)

        while True:
            schedule.run_pending()
            time.sleep(1)

    @staticmethod
    def login_into_class(username, password, link, login_mode):

        username_input = App.browser.find_element_by_xpath(
            "/html/body/div[1]/div[1]/div/div/div[3]/div/div/form/div[1]/input"
        )
        password_input = App.browser.find_element_by_xpath(
            "/html/body/div[1]/div[1]/div/div/div[3]/div/div/form/div[2]/input"
        )
        guess_button = App.browser.find_element_by_xpath('//*[@id="btn_guest"]')

        if login_mode == "account":
            username_input.send_keys(username)
            password_input.send_keys(password)
            password_input.send_keys(Keys.ENTER)
        else:
            try:
                guess_button.click()
                time.sleep(7)
                guess_name = App.browser.find_element_by_xpath(
                    "/html/body/div[5]/div[2]/div/input"
                )
                guess_name.send_keys(username)
                guess_name.send_keys(Keys.ENTER)
            except Exception:
                pass
        time.sleep(5)

        while True:

            warning = App.browser.find_element_by_class_name("warning").text

            if warning == "":
                break

            elif warning == "نام کاربری پیدا نشد.":
                print("ERROR : user not  found ,please try again")
                App.browser.refresh()
                App.username_password()
                App.login_into_class(App.username, App.password, link)

            elif warning == "شما دسترسی لازم برای ورود به اتاق را ندارید.":
                print(
                    "ERROR : You don't have Permission to login try again with another teacher and password".title()
                )

                username = password = ""
                App.browser.refresh()
                App.login_into_class(username, password, link)

            elif (
                warning
                == "اپراتور هنوز وارد نشده است. به محض ورود اپراتور، به صورت خودکار به اتاق هدایت خواهید شد. لطفا منتظر بمانید..."
            ):
                print(
                    "ERROR : opreator Dose not logged in yet trying again after 5 seconds"
                )
            else:
                print("an error ecoored\nTrying again ...")
                time.sleep(5)
                App.browser.refresh()
                App.login_into_class(username, password, link)

        massage_box = App.browser.find_element_by_xpath(
            "/html/body/div[2]/div[1]/div[2]/div[1]/div[4]/div[2]/div/div[2]/div[3]/div[1]"
        )
        massage_box.send_keys("سلام استاد خسته نباشید")
        massage_box.send_keys(Keys.ENTER)
        App.save_snapshot()

    @staticmethod
    def save_snapshot():

        if not os.path.exists("screenshouts"):
            os.makedirs("screenshouts")
        file_name = time.strftime("%Y%m%d-%H%M%S")
        App.browser.save_screenshot(f"./screenshouts/{file_name}.png")


if __name__ == "__main__":
    app = App()
