from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import pyautogui
import credentials
from selenium.webdriver.support.ui import WebDriverWait


class ConnectionRequest:
    def __init__(self, driver):
        self.driver = driver

    def find_follow_and_connect(self):
        follow_Found = False
        connect_Found = False
        more_Found = False
        isConnectClicked = False
        isFollowClicked = False
        mainDivs = None
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'pv-top-card-v2-ctas')))
        except Exception as e:
            print(str(e))
            pass
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

        if mainDivs:
            for div in mainDivs:
                try:
                    if not follow_Found and div and div.text == 'Follow':
                        isFollowClicked = self.btnFollowFound(div)
                        follow_Found = True
                        time.sleep(random.uniform(1, 1.5))
                    if not connect_Found and div and div.text == 'Connect':
                        isConnectClicked = self.btnConnectFound(div)
                        connect_Found = True
                        time.sleep(random.uniform(1, 1.5))
                    if not more_Found and div and div.text == 'More':
                        self.more_Found(div, isConnectClicked, isFollowClicked)
                except:
                    pass
        if not isConnectClicked or not isFollowClicked:
            return False

    def more_Found(self, btnMore, isConnectClicked, isFollowClicked):
        try:
            time.sleep(random.uniform(.7, 1))
            self.click_using_mouse_move(btnMore.find_element(
                By.TAG_NAME, 'button'), 1)
            time.sleep(random.uniform(.7, 1))
            lis = btnMore.find_elements(By.TAG_NAME, 'li')
            if lis:
                for li in lis:
                    try:
                        if not isConnectClicked and li and li.text == 'Connect':
                            self.btnConnectFound(li)
                        if not isFollowClicked and li and li.text == 'Follow':
                            self.btnFollowFound(li)
                    except:
                        pass
        except Exception as e:
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
        return True

    def click_using_mouse_move(self, element, isscript=0):
        try:
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
                return True
            else:
                time.sleep(random.uniform(.3, .5))
                self.driver.execute_script(
                    "arguments[0].click();", element)
                return True
        except:
            return False

    def btnFollowFound(self, btnConnect):
        return self.click_using_mouse_move(btnConnect)

    def btnConnectFound(self, btnConnect):
        if self.click_using_mouse_move(btnConnect):
            return self.send_connection_request()
