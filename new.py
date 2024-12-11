import os
import json
from cryptography.fernet import Fernet
from tkinter import messagebox
from tkinter import Tk, Label, Entry, Button, StringVar, Toplevel, OptionMenu
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class UserManager:
    def __init__(self, user_file="user.json"):
        self.user_file = user_file
        
    def load_accounts(self, platform):
        raise NotImplementedError("load_accounts 메서드는 UserManager 클래스에서 구현되어야 합니다.")
        
    def register_user(self, user_id, password):
        """새로운 사용자 등록"""
        data = {}
        if os.path.exists(self.user_file):
            with open(self.user_file, "r") as file:
                data = json.load(file)

        if user_id in data:
            return False  
        
        data[user_id]=password
        with open(self.user_file, "w") as file:
            json.dump(data, file)
        return True

    def authenticate_user(self, user_id, password):
        """사용자 인증"""
        if not os.path.exists(self.user_file):
            return False

        with open(self.user_file, "r") as file:
            data = json.load(file)

        if user_id in data:
            login_password = data[user_id]
            return password == login_password
        return False
    
    def get_user(self, user_id):
        if not os.path.exists(self.user_file):
            return None
        with open(self.user_file, "r") as file:
            data = json.load(file)
        if user_id in data:
            return user_id
        return None

class OTTAccountManager(UserManager):
    def __init__(self,account_file="OttAcount.json"):
        self.accounts=account_file

    def load_accounts(self,user, platform):
        """OTT 계정을 불러옴"""
        if not os.path.exists(self.accounts):
            return None, None
        with open(self.accounts, "r") as file:
            data = json.load(file)
        if platform not in data.get(user, {}):
            print(f"{platform} 계정 정보가 없습니다.")
            return None, None
        email= data[user][platform]["email"]
        password= data[user][platform]["password"]
        return email, password
    
    def save_account(self,user, platform, email, password):
        """OTT 계정을 저장함"""
        data = {}
        if os.path.exists(self.accounts):
            with open(self.accounts, "r") as file:
                data = json.load(file)
        if user not in data:
            data[user] = {}
        print(f"User:{user})")
        data[user][platform] = {"email": email, "password": password}
        with open(self.accounts, "w") as file:
            json.dump(data, file, indent=4)
        messagebox.showinfo("Success", f"{platform} 계정 정보 저장 완료!")
    
    def modify_account(self):
        current_user = temp_login_data
        def on_platform_select(*args):
            email, password = self.load_accounts(current_user, platform_var.get())
            email_var.set(email if email else "")
            password_var.set(password if password else "")
        
        modify_window = Toplevel()
        modify_window.title("계정정보 수정")
        modify_window.geometry("400x300")
        Label(modify_window, text="플랫폼 선택", font=("bold", 12)).pack(pady=5)
        platform_var= StringVar(modify_window)
        platform_var.set("Netflix")
        platform_var.trace_add("write", on_platform_select)
        platforms = ["Netflix", "Disney+", "Tving", "Coupang Play"]
        
        def save_changes():
            current_user = temp_login_data
            platform = platform_var.get()
            email = email_var.get()
            password = password_var.get()
            
            if not email or not password:
                messagebox.showerror("Error", "이메일과 비밀번호를 입력하세요!")
                return
            self.save_account(current_user,platform, email, password)
            modify_window.destroy()
            
        Label(modify_window, text="이메일", font=("Arial", 14)).pack(pady=5)
        email_var = StringVar(modify_window)
        Entry(modify_window, textvariable=email_var, 
              font=("Arial", 14)).pack(pady=5)
        
        Label(modify_window, text="비밀번호", font=("Arial", 14)).pack(pady=5)
        password_var = StringVar(modify_window)
        Entry(modify_window, textvariable=password_var, show="*").pack(pady=5)
        
        Button(modify_window, text="저장", font=("Arial", 14),
               command=save_changes).pack(pady=5)
        
        OptionMenu(modify_window, platform_var, *platforms).pack(pady=5)


def show_login_window():
    def login():
        global temp_login_data
        user_id = id_var.get()
        password = password_var.get()

        if not user_id or not password:
            messagebox.showerror("Error", "ID와 비밀번호를 입력하세요!")
            return

        if user_manager.authenticate_user(user_id, password):
            current_user = user_id
            messagebox.showinfo("Success", "로그인 성공!")
            temp_login_data=user_id
            login_window.destroy()
            create_gui(app, account_manager)
        else:
            messagebox.showerror("Error", "ID 또는 비밀번호가 잘못되었습니다.")

    def register():
        user_id = id_var.get()
        password = password_var.get()

        if not user_id or not password:
            messagebox.showerror("Error", "ID와 비밀번호를 입력하세요!")
            return

        if user_manager.register_user(user_id, password):
            messagebox.showinfo("Success", "사용자가 성공적으로 등록되었습니다!")
        else:
            messagebox.showerror("Error", "이미 존재하는 ID입니다.")

    login_window = Tk()
    login_window.title("로그인")
    login_window.geometry("300x200")

    id_var = StringVar()
    password_var = StringVar()

    Label(login_window, text="ID").pack(pady=5)
    Entry(login_window, textvariable=id_var).pack(pady=5)

    Label(login_window, text="비밀번호").pack(pady=5)
    Entry(login_window, textvariable=password_var, show="*").pack(pady=5)

    Button(login_window, text="로그인", command=login).pack(pady=5)
    Button(login_window, text="회원가입", command=register).pack(pady=5)

    login_window.mainloop()
    
class App(OTTAccountManager):
    def __init__(self,account_file="OttAcount.json"):
        self.driver=None
        self.accounts=account_file
    
    def getdriver(self):
        if self.driver is None:
            self.driver = webdriver.Chrome()
        return self.driver
    
    def login_to_platform(self, platform):
        current_user = temp_login_data
        email,password=super().load_accounts(current_user, platform)
        if not email or not password:
            messagebox.showerror("Error", 
                                 f"{platform}계정 정보가 없습니다! 계정을 등록하세요.")
            return
        driver = self.getdriver()
        try:
            if platform == "Netflix":
                driver.get("https://www.netflix.com/kr/login/")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, ":r0:"))
                ).send_keys(email)
                driver.find_element(By.ID, ":r3:").send_keys(password)
                driver.find_element(By.XPATH,
                '//*[@id="appMountPoint"]/div/div/div[2]/div/form/button[1]').click()
            
            elif platform == "Disney+":
                driver.get("https://www.disneyplus.com/ko-kr/login")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "email"))
                ).send_keys(email)
                driver.find_element(By.XPATH,
                '//*[@id="global-identity-ui"]/div/div/div/div[2]/div/form/button').click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "password"))
                ).send_keys(password)
                driver.find_element(By.XPATH,
                '//*[@id="global-identity-ui"]/div/div/div/div[2]/div/form/button').click()
            elif platform == "Tving":
                driver.get("https://www.tving.com/account/login/tving?returnUrl=https%3A%2F%2Fwww.tving.com")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, ":R56fnnija:-form-item"))
                ).send_keys(email)
                driver.find_element(By.ID, ":R96fnnija:-form-item").send_keys(password)
                driver.find_element(By.XPATH,
                '/html/body/div[1]/main/div/div/div[2]/form/button').click()    
        
        except Exception as e:
            messagebox.showerror("Error", f"{platform} 로그인 중 오류 발생!")
    
    def on_close(self):
        if self.driver:
            self.driver.quit()

def show_main_application():
    def save_account():
        platform = platform_var.get()
        email = email_var.get()
        password = password_var.get()
        current_user = temp_login_data

        if not platform or not email or not password:
            messagebox.showerror("Error", "모든 필드를 입력하세요!")
            return

        account_manager.save_account(current_user, platform, email, password)
        messagebox.showinfo("Success", f"{platform} 계정 저장 완료!")

    def delete_account():
        platform = platform_var.get()
        account_manager.delete_account(platform)
        messagebox.showinfo("Success", f"{platform} 계정 삭제 완료!")

    # 현재 로그인한 사용자별로 OTT 계정 관리 객체 생성
    account_manager = OTTAccountManager()

    main_window = Toplevel()
    main_window.title("OTT 계정 관리")
    main_window.geometry("400x300")

    platform_var = StringVar()
    email_var = StringVar()
    password_var = StringVar()

    Label(main_window, text="플랫폼").pack(pady=5)
    Entry(main_window, textvariable=platform_var).pack(pady=5)

    Label(main_window, text="이메일").pack(pady=5)
    Entry(main_window, textvariable=email_var).pack(pady=5)

    Label(main_window, text="비밀번호").pack(pady=5)
    Entry(main_window, textvariable=password_var, show="*").pack(pady=5)

    Button(main_window, text="저장", command=save_account).pack(pady=5)
    Button(main_window, text="삭제", command=delete_account).pack(pady=5)
    main_window.mainloop()
    
def create_gui(app, account_manager):
    current_user = temp_login_data
    def on_button_click(platform):
        email, password = account_manager.load_accounts(current_user, platform)
        if not email or not password:
            messagebox.showerror("Error", f"{platform} 계정 정보가 없습니다!")
        elif email is None or password is None:
            messagebox.showerror("Error", f"{platform} 지원되지 않습니다!")
            return
        else:
            app.login_to_platform(platform)
        
    root = Tk()
    root.title("OTT Auto Login")
    root.geometry("400x400")
    Label(root, text="OTT 플랫폼 선택", font=("Arial", 16)).pack(pady=20)
    platforms = ["Netflix", "Disney+", "Tving", "Coupang Play"]
    for platform in platforms:
        Button(
            root, text=platform, font=("Arial", 14), width=20, 
            command=lambda p=platform: on_button_click(p)
        ).pack(pady=10)
            
    Button(root,
            text="계정 수정", font=("Arial", 14), 
            command=account_manager.modify_account).pack(pady=10)
        
    root.mainloop()
        
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
    
if __name__ == "__main__":
    global temp_login_data
    user_manager = UserManager()
    account_manager=OTTAccountManager()
    app=App()
    show_login_window()