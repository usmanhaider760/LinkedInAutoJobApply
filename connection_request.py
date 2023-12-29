from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import pyautogui
import credentials


class ConnectionRequest:
    def __init__(self, driver):
        self.driver = driver

    def find_follow_and_connect(self):
        follow_Found = False
        connect_Found = False
        more_Found = False
        mainDivs = None
        try:
            mainDivs = self.driver.find_element(
                By.XPATH, '/html/body/div[4]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[3]/div').find_elements(By.XPATH, '*')
        except:
            mainDivs = None
            pass
        try:
            mainDivs = self.driver.find_element(
                By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[3]/div').find_elements(By.XPATH, '*')
        except:
            mainDivs = None
            pass

        if not mainDivs:
            for div in mainDivs:
                try:
                    if not follow_Found and div[0] and div[0].text == 'Follow':
                        self.btnFollowFound(div[0])
                        follow_Found = True
                    if not connect_Found and div[0] and div[0].text == 'Connect':
                        self.btnConnectFound(div[0])
                        connect_Found = True
                    if not more_Found and div[0] and div[0].text == 'More':
                        self.more_Found()
                        connect_Found = True
                except:
                    pass

    def more_Found(self, btnMore, isConnectClicked, isFollowClicked):
        found = True
        if not found:
            try:
                time.sleep(random.uniform(.7, 1))
                self.click_using_mouse_move(btnMore, 1)
                time.sleep(random.uniform(.7, 1))
                btnConnect = self.driver.find_element(
                    By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[3]/div/div[2]/div/div/ul/li[3]/div')
                if btnConnect:
                    self.click_using_mouse_move(btnConnect, 1)
                    found = True
            except Exception as e:
                pefoundrf = False
                print(str(e))
                pass
        if not found:
            try:
                btnSecondConnect = self.driver.find_element(
                    By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[3]/div/button')
                if btnSecondConnect:
                    time.sleep(random.uniform(.7, 1))
                    self.click_using_mouse_move(btnSecondConnect, 1)
                    time.sleep(random.uniform(.7, 1))
                    found = True
            except Exception as e:
                pefoundrf = False
                print(str(e))
                pass
        time.sleep(random.uniform(1.5, 2))

    def send_connection_request(self):
        try:
            To_verify_this_member_knows_you = self.driver.find_element(
                By.XPATH, '/html/body/div[3]/div/div/div[2]/label')
            if To_verify_this_member_knows_you and 'To verify this member knows you, please enter their email to connect' in To_verify_this_member_knows_you.text:
                txta = self.driver.find_element(
                    By.XPATH, '/html/body/div[3]/div/div/div[2]/label/input')
                if txta:
                    txta.send_keys(credentials.email)
        except:
            pass
        send_without_a_note = self.driver.find_element(
            By.XPATH, '/html/body/div[3]/div/div/div[3]/button[2]')
        if send_without_a_note and send_without_a_note.text == 'Send without a note':
            self.click_using_mouse_move(send_without_a_note)
        time.sleep(random.uniform(1.5, 2))

    def click_using_mouse_move(self, element, isscript=0):
        location = element.location
        size = element.size
        # Calculate the coordinates of the center of the element
        x = location['x'] + size['width'] // 2
        y = location['y'] + size['height'] // 2
        pyautogui.moveTo(x, y, duration=random.uniform(.4, .8))
        if isscript == 0:
            # pyautogui.click()
            time.sleep(random.uniform(.3, .5))
            element.click()
        else:
            time.sleep(random.uniform(.3, .5))
            self.driver.execute_script(
                "arguments[0].click();", element)

    def btnFollowFound(self, btnConnect):
        self.click_using_mouse_move(btnConnect)

    def btnConnectFound(self, btnConnect):
        self.click_using_mouse_move(btnConnect)
        self.send_connection_request()
