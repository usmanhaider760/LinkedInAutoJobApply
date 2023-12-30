import time
import math
import random
import os
import utils
import constants
import config
import credentials
import pickle
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import colorama
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import time
from langdetect import detect
from googletrans import Translator
import csv
from datetime import datetime
import pyautogui
from connection_request import ConnectionRequest
from selenium.common.exceptions import NoSuchElementException


class Linkedin:
    def __init__(self):
        self.today_date = datetime.today().strftime('%Y%m%d')
        self.driver = webdriver.Chrome(service=ChromeService(
            ChromeDriverManager().install()), options=utils.chromeBrowserOptions())
        self.cookies_path = f"{os.path.join(os.getcwd(),'cookies')}/{self.getHash(credentials.email)}.pkl"
        self.driver.get('https://www.linkedin.com')
        self.loadCookies()
        self.WebDriverWait = WebDriverWait
        self.csv_link_profile_file = 'profile_links.csv'
        self.csv_link_job_file = f'job_links_{self.today_date}.csv'
        self.connection_request_instance = ConnectionRequest(self.driver)
        pyautogui.FAILSAFE = False
        if not self.isLoggedIn():
            self.driver.get(
                "https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")
            utils.prGreen(
                "✅ Trying to log in Linkedin...")
            try:
                try:
                    self.driver.find_element(
                        "id", "username").send_keys(credentials.email)
                except:
                    pass
                # time.sleep(2)
                try:
                    self.driver.find_element(
                        "id", "password").send_keys(credentials.password)
                except:
                    pass
                # time.sleep(2)
                try:
                    self.click_using_mouse_move(self.driver.find_element(
                        "xpath", '//button[@type="submit"]'))
                except:
                    pass
                time.sleep(10)
            except:
                utils.prRed(
                    "❌ Couldn't log in Linkedin by using Chrome. Please check your Linkedin credentials on config files line 7 and 8.")

            self.saveCookies()
        # start application
        self.linkJobApply()

    def getHash(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    def loadCookies(self):
        if os.path.exists(self.cookies_path):
            cookies = pickle.load(open(self.cookies_path, "rb"))
            self.driver.delete_all_cookies()
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def saveCookies(self):
        cookies_dir = os.path.dirname(self.cookies_path)
        if not os.path.exists(cookies_dir):
            os.makedirs(cookies_dir)
        pickle.dump(self.driver.get_cookies(), open(self.cookies_path, "wb"))

    def isLoggedIn(self):
        self.driver.get('https://www.linkedin.com/feed')
        try:
            self.driver.find_element(By.XPATH, '//*[@id="ember14"]')
            return True
        except:
            pass
        return False

    def generateUrls(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        try:
            with open('data/urlData.txt', 'w', encoding="utf-8") as file:
                linkedinJobLinks = utils.LinkedinUrlGenerate().generateUrlLinks()
                for url in linkedinJobLinks:
                    file.write(url + "\n")
            utils.prGreen(
                "✅ Apply urls are created successfully, now the bot will visit those urls.")
        except:
            utils.prRed(
                "❌ Couldn't generate urls, make sure you have editted config file line 25-39")

    def linkJobApply(self):
        self.generateUrls()
        countApplied = 0
        countJobs = 0

        urlData = utils.getUrlDataFile()

        for url in urlData:
            self.driver.get(url)
            time.sleep(random.uniform(1, constants.botSpeed))
            totalJobs = None
            totalPages = None
            try:
                totalJobs = self.driver.find_element(By.XPATH, '//small').text
                totalPages = utils.jobsToPages(totalJobs)
            except:
                totalJobs = None
                totalPages = None
                pass

            if not totalJobs == None and not totalPages == None:
                urlWords = utils.urlToKeywords(url)
                lineToWrite = "\n✅ Category: " + \
                    urlWords[0] + ", Location: " + urlWords[1] + \
                    ", Applying " + str(totalJobs) + " jobs."
                self.displayWriteResults(lineToWrite)

                for page in range(totalPages):
                    currentPageJobs = constants.jobsPerPage * page
                    url = url + "&start=" + str(currentPageJobs)
                    self.driver.get(url)
                    time.sleep(random.uniform(1, constants.botSpeed))
                    offersPerPage = []
                    offersPerPageFilter = self.driver.find_elements(
                        By.XPATH, '//li[@data-occludable-job-id]')
                    for li_element in offersPerPageFilter:
                        try:
                            li_element.find_element(
                                By.XPATH, './/span[contains(text(), "Applied")]')
                        except NoSuchElementException:
                            offersPerPage.append(li_element)
                    offerIds = [(offer.get_attribute(
                        "data-occludable-job-id").split(":")[-1]) for offer in offersPerPage]
                    time.sleep(random.uniform(1, constants.botSpeed))

                    for jobID in offerIds:
                        offerPage = 'https://www.linkedin.com/jobs/view/' + \
                            str(jobID)
                        if not self.isUrlExist(offerPage):
                            self.driver.get(offerPage)
                            time.sleep(random.uniform(1, constants.botSpeed))

                            countJobs += 1

                            jobProperties = self.getJobProperties(countJobs)
                            if "blacklisted" in jobProperties:
                                lineToWrite = '✅ '+jobProperties + " | " + \
                                    "*                            🤬 Blacklisted Job, skipped!: "  \
                                    + str(offerPage)
                                self.displayWriteResults(lineToWrite)

                            else:
                                easyApplybutton = self.easyApplyButton()

                                if easyApplybutton is not False:
                                    self.click_using_mouse_move(
                                        easyApplybutton)
                                    time.sleep(random.uniform(
                                        1, constants.botSpeed))
                                    countApplied += 1
                                    try:
                                        self.chooseResume()
                                        self.click_using_mouse_move(self.driver.find_element(
                                            By.CSS_SELECTOR, "button[aria-label='Submit application']"))
                                        time.sleep(random.uniform(
                                            1, constants.botSpeed))

                                        lineToWrite = "🥳 Just Applied to this job: "  \
                                            + str(offerPage)
                                        self.check_and_update_job_link_csv(
                                            offerPage, self.csv_link_job_file, True)
                                        self.displayWriteResults(lineToWrite)

                                    except:
                                        try:
                                            self.Continue_to_next_step()
                                            time.sleep(random.uniform(
                                                1, constants.botSpeed))
                                            self.chooseResume()
                                            comPercentage = self.driver.find_element(
                                                By.XPATH, 'html/body/div[3]/div/div/div[2]/div/div/span').text
                                            percenNumber = int(
                                                comPercentage[0:comPercentage.index("%")])
                                            result = self.applyProcess(
                                                percenNumber, offerPage)
                                            lineToWrite = '✅ '+jobProperties + " | " + result
                                            self.displayWriteResults(
                                                lineToWrite)

                                        except Exception:
                                            self.chooseResume()
                                            lineToWrite = "🥵 Cannot apply to this Job! " \
                                                + str(offerPage)
                                            self.check_and_update_job_link_csv(
                                                offerPage, self.csv_link_job_file, False)
                                            self.displayWriteResults(
                                                lineToWrite)
                                else:
                                    lineToWrite = '✅ '+jobProperties + " | " + \
                                        "*                            🥳 Already applied! Job: "  \
                                        + str(offerPage)
                                    self.displayWriteResults(lineToWrite)
                            self.navigate_to_person_profile()

                utils.prYellow("✅  Category: " + urlWords[0] + "," + urlWords[1] + " applied: " + str(countApplied) +
                               " jobs out of " + str(countJobs) + ".")

    def chooseResume(self):
        try:
            self.driver.find_element(
                By.CLASS_NAME, "jobs-document-upload__title--is-required")
            resumes = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'ui-attachment--pdf')]")
            if (len(resumes) == 1 and resumes[0].get_attribute("aria-label") == "Select this resume"):
                self.click_using_mouse_move(resumes[0])
            elif (len(resumes) > 1 and resumes[config.preferredCv-1].get_attribute("aria-label") == "Select this resume"):
                self.click_using_mouse_move(resumes[config.preferredCv-1])
            elif (type(len(resumes)) != int):
                utils.prRed(
                    "❌ No resume has been selected please add at least one resume to your Linkedin account.")
        except:
            pass

    def getJobProperties(self, count):
        textToWrite = ""
        jobTitle = ""
        jobLocation = ""

        try:
            jobTitle = self.driver.find_element(
                By.XPATH, "//h1[contains(@class, 'job-title')]").get_attribute("innerHTML").strip()
            res = [blItem for blItem in config.blackListTitles if (
                blItem.lower() in jobTitle.lower())]
            if (len(res) > 0):
                jobTitle += "(blacklisted title: " + ' '.join(res) + ")"
        except Exception as e:
            if (config.displayWarnings):
                utils.prYellow(
                    "⚠️ Warning in getting jobTitle: " + str(e)[0:50])
            jobTitle = ""

        try:
            time.sleep(random.uniform(3, 5))
            jobDetail = self.driver.find_element(
                By.XPATH, "//div[contains(@class, 'job-details-jobs')]//div").text.replace("·", "|")
            res = [blItem for blItem in config.blacklistCompanies if (
                blItem.lower() in jobTitle.lower())]
            if (len(res) > 0):
                jobDetail += "(blacklisted company: " + ' '.join(res) + ")"
        except Exception as e:
            if (config.displayWarnings):
                print(e)
                utils.prYellow(
                    "⚠️ Warning in getting jobDetail: " + str(e)[0:100])
            jobDetail = ""

        try:
            jobWorkStatusSpans = self.driver.find_elements(
                By.XPATH, "//span[contains(@class,'ui-label ui-label--accent-3 text-body-small')]//span[contains(@aria-hidden,'true')]")
            for span in jobWorkStatusSpans:
                jobLocation = jobLocation + " | " + span.text

        except Exception as e:
            if (config.displayWarnings):
                print(e)
                utils.prYellow(
                    "⚠️ Warning in getting jobLocation: " + str(e)[0:100])
            jobLocation = ""

        textToWrite = str(count) + " | " + jobTitle + \
            " | " + jobDetail + jobLocation
        return textToWrite

    def easyApplyButton(self):
        try:
            # self.driver.get(
            #     'https://www.linkedin.com/jobs/view/3786700782/')
            time.sleep(random.uniform(1, constants.botSpeed))
            button = self.driver.find_element(
                By.XPATH, "//div[contains(@class,'jobs-apply-button--top-card')]//button[contains(@class, 'jobs-apply-button')]")
            EasyApplyButton = button
        except:
            EasyApplyButton = False

        return EasyApplyButton

    def applyProcess(self, percentage, offerPage):
        applyPages = math.floor(100 / percentage) - 2
        result = ""
        for pages in range(applyPages):
            self.Continue_to_next_step()
            self.checkIfQuestionSectionExist()
            self.Continue_to_next_step()
        self.click_using_mouse_move(self.driver.find_element(
            By.CSS_SELECTOR, "button[aria-label='Review your application']"))
        time.sleep(random.uniform(1, constants.botSpeed))

        if config.followCompanies is False:
            try:
                checkbox = self.driver.find_element(
                    By.ID, "follow-company-checkbox")
                if not checkbox.is_selected():
                    self.click_using_mouse_move(checkbox)
                # self.click_using_mouse_move(self.driver.find_element(
                #     By.CSS_SELECTOR, "label[for='follow-company-checkbox']"))
            except:
                pass

        self.click_using_mouse_move(self.driver.find_element(
            By.CSS_SELECTOR, "button[aria-label='Submit application']"))
        time.sleep(random.uniform(1, constants.botSpeed))

        result = "*                            🥳 Just Applied to this job: "  \
            + str(offerPage)

        return result

    def displayWriteResults(self, lineToWrite: str):
        try:
            print(lineToWrite)
            utils.writeResults(lineToWrite)
        except Exception as e:
            utils.prRed(
                "❌ Error in DisplayWriteResults: " + str(e))

    def checkIfQuestionSectionExist(self):  # check if question exist
        try:
            Additional_Questions = self.driver.find_element(
                By.XPATH, "html/body/div[3]/div/div/div[2]/div/div[2]/form/div/div/h3")
            lang = detect(Additional_Questions.text)
            if lang != 'en':
                translator = Translator()
                translation = translator.translate(
                    Additional_Questions.text, dest='en')
                translated_word = translation.text
            if (' Questions'.lower() in translated_word.lower()) or 'Additional'.lower() in translated_word.lower():
                if not os.path.exists('Q_A_File'):
                    pd.DataFrame(columns=['Question', 'Answer']).to_csv(
                        'Q_A_File', index=False)

                all_parent_questions_div = self.driver.find_element(
                    By.XPATH, '/html/body/div[3]/div/div/div[2]/div/div[2]/form/div/div')
                all_questions_div = all_parent_questions_div.find_elements(
                    By.XPATH, './div')
                for index, question_element in enumerate(all_questions_div):
                    self.answerThe_Question(question_element, index+1)

            try:
                chkAgree = self.driver.find_element(
                    By.XPATH, '/html/body/div[3]/div/div/div[2]/div/div[2]/form/div/div/div[8]/div/fieldset/div/input')
                if chkAgree and chkAgree.get_attribute("type") == "checkbox":
                    if not chkAgree.is_selected():
                        self.click_using_mouse_move(chkAgree, 1)

            except:
                pass

        except Exception as e:
            utils.prRed(
                "❌ Error in DisplayWriteResults: " + str(e))

    def answerThe_Question(self, question_element, index):
        try:
            try:
                fieldset = question_element.find_element(
                    By.TAG_NAME, 'fieldset')
            except:
                fieldset = None
                pass
            try:
                textBox = question_element.find_element(
                    By.CSS_SELECTOR, 'input[type="text"]')
            except:
                textBox = None
                pass
            try:
                selectionOption = question_element.find_element(
                    By.CSS_SELECTOR, '[data-test-text-entity-list-form-component]')
            except:
                selectionOption = None
                pass
            result = False

            if fieldset:
                isRadio = fieldset.find_element(
                    By.TAG_NAME, 'input').get_attribute("type") == "radio"
                if isRadio:
                    result = self.isRadioQuestion(fieldset, index)
            if textBox:
                result = self.isTextBoxQuestion(question_element, index)
            if selectionOption:
                result = self.isSelectionQuestion(question_element, index)
            print(result)
        except:
            pass

    def isRadioQuestion(self, fieldset, index):
        questions_and_answers = self.read_questions_and_answers()
        try:
            question_span = WebDriverWait(fieldset, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'span[aria-hidden="true"]'))
            )
            question_text = question_span.text.strip()

            if question_text and question_text in questions_and_answers:
                answer = questions_and_answers[question_text]
                if answer:
                    radio_inputs = WebDriverWait(fieldset, 10).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, 'input[type="radio"]'))
                    )

                    for radio_input in radio_inputs:
                        try:
                            label_for_radio = fieldset.find_element(
                                By.XPATH, f'.//input[@id="{radio_input.get_attribute("id")}"]/following::label')

                            # Hover over the radio input to make it visible and clickable
                            ActionChains(self.driver).move_to_element(
                                radio_input).perform()
                            time.sleep(random.uniform(.2, .6))

                            if label_for_radio.text.strip() in answer:
                                self.click_using_mouse_move(radio_input, 1)
                                return True

                        except Exception as e:
                            utils.prRed(
                                "❌ Error in Radio Button Check: " + str(e))
            else:
                self.answer_Not_Found(question_text)
                self.isRadioQuestion(fieldset, index)
            return False

        except Exception as e:
            utils.prRed("❌ Error in retrieving question text: " + str(e))
            return False

    def isTextBoxQuestion(self, question_element, index):
        try:
            questions_and_answers = self.read_questions_and_answers()

            # Wait for the question label to be present
            question_label = WebDriverWait(question_element, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'label.artdeco-text-input--label'))
            )

            question_text = question_label.text.strip()
            if question_text in questions_and_answers:
                # Wait for the input element to be present
                input_ans = WebDriverWait(question_element, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'input[type="text"]'))
                )

                if input_ans:
                    input_ans_value = input_ans.get_attribute("value")

                    if input_ans_value is None or input_ans_value == "0" or input_ans_value.strip() == '':
                        answer = questions_and_answers[question_text]
                        input_ans.send_keys(answer)
                        return True
            else:
                self.answer_Not_Found(question_text)
                self.isTextBoxQuestion(question_element, index)

        except Exception as e:
            utils.prRed("❌ Error in isTextBoxQuestion: " + str(e))
            return False

    def isSelectionQuestion(self, question_element, index):
        try:
            questions_and_answers = self.read_questions_and_answers_GroupBy()
            questionLabel = question_element.find_element(
                By.CSS_SELECTOR, 'span[aria-hidden="true"]')
            question_text = questionLabel.text
            answer = self.checkSelection_options_answers(
                question_text, questions_and_answers, question_element)
            if answer is not None:
                select_element = question_element.find_element(
                    By.TAG_NAME, 'select')
                self.click_using_mouse_move(select_element)
                select = Select(select_element)
                desired_value = answer
                for option in select.options:
                    if option.get_attribute("value") == desired_value:
                        select.select_by_value(desired_value)
                        return True
            else:
                self.answer_Not_Found(question_text, question_element)
                self.isSelectionQuestion(question_element, index)

        except Exception as e:
            utils.prRed("❌ Error in Selection: " + str(e))
            return False

    def checkSelection_options_answers(self, question_text, questions_and_answers, question_element=None):
        matchedAns = None
        if question_element is not None:
            select_element = question_element.find_element(
                By.TAG_NAME, 'select')
            self.click_using_mouse_move(select_element)
            select = Select(select_element)
            matching_rows = questions_and_answers.get(question_text, [])
            for answerRow in matching_rows:
                if matchedAns is None:
                    for option in select.options:
                        if matchedAns is None:
                            if option.get_attribute("value") == answerRow:
                                matchedAns = answerRow
                                break
                        else:
                            break
                else:
                    break

        return matchedAns

    def answer_Not_Found(self, question, question_element=None):
        lang = detect(question)
        if lang != 'en':
            translator = Translator()
            translation = translator.translate(question, dest='en')
            translated_word = translation.text
        else:
            # If the language is already English, use the original question
            translated_word = question
        if question_element is not None:
            select_element = question_element.find_element(
                By.TAG_NAME, 'select')
            self.click_using_mouse_move(select_element)
            select = Select(select_element)
            answer_Options = None
            answer_Options = ', '.join(option.get_attribute(
                "value") for option in select.options)
            utils.prYellow(answer_Options)
        _input = 'Question: ' + translated_word + '\n'
        user_input = input(f"\033[92m{_input}\033[00m")
        processed_output = f"{user_input}"
        # Corrected file extension to '.csv'
        existing_df = pd.read_csv(
            'Q_A_File', encoding='utf-8', na_values=['None'])
        new_data = {'Question': [question], 'Answer': [processed_output]}
        new_df = pd.DataFrame(new_data)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        # Corrected file extension to '.csv'
        updated_df.to_csv('Q_A_File', index=False)

    def isUrlExist(self, jobUrl):
        job_urls_file = 'job_urls.txt'
        # 1. Check if job_urls file exists, create if not
        if not os.path.exists(job_urls_file):
            with open(job_urls_file, 'w') as file:
                pass  # Create an empty file if it doesn't exist
        # 2. Check if a URL exists
        with open(job_urls_file, 'r') as file:
            existing_urls = file.read().splitlines()
            if jobUrl in existing_urls:
                return True
        # 3. If the URL doesn't exist, write it to the file

        with open(job_urls_file, 'a') as file:
            file.write(jobUrl + '\n')
            return False

    def write_Job_Url(self, jobUrl):
        job_urls_file = 'job_urls.txt'
        # 1. Check if job_urls file exists, create if not
        if not os.path.exists(job_urls_file):
            with open(job_urls_file, 'w') as file:
                pass  # Create an empty file if it doesn't exist
        with open(job_urls_file, 'a') as file:
            file.write(jobUrl + '\n')
            return False

    def read_questions_and_answers(self):
        try:
            data = pd.read_csv('Q_A_File', encoding='utf-8',
                               na_values=['None'])
            questions = data['Question'].tolist()
            answers = data['Answer'].tolist()
            return dict(zip(questions, answers))
        except FileNotFoundError:
            return {}

    def read_questions_and_answers_GroupBy(self):
        try:
            data = pd.read_csv('Q_A_File', encoding='utf-8',
                               na_values=['None'])
            grouped_data = data.groupby(
                'Question')['Answer'].apply(list).reset_index()
            questions_and_answers = dict(
                zip(grouped_data['Question'], grouped_data['Answer']))
            return questions_and_answers
        except FileNotFoundError:
            return {}

    # Function to write a new question and answer to CSV
    def write_question_and_answer(self, question, answer):
        data = pd.DataFrame({'Question': [question], 'Answer': [answer]})
        data.to_csv('Q_A_File', mode='a', header=False, index=False)

    def colored_input(self, question):
        colorama.init()
        RED = '\033[91m'
        RESET = '\033[0m'
        QUESTION_ICON = '❓'
        BIG_FONT = '\033[8;20;20t'
        colored_question = f'{BIG_FONT}{RED}{QUESTION_ICON} {question}{RESET} '
        return input(colored_question)

    def navigate_to_person_profile(self):
        found = True
        try:
            closeDonePopup = self.click_using_mouse_move(self.driver.find_element(
                By.XPATH, '/html/body/div[3]/div/div/div[3]/button'))
        except:
            pass

        try:
            profileLink = self.driver.find_element(
                By.XPATH, '/html/body/div[5]/div[3]/div[2]/div/div/main/div/div[1]/div/div[2]/div/div/div[2]/a')
            if profileLink and 'https://www.linkedin.com' in profileLink.get_attribute('href'):
                found = True
            else:
                found = False
        except:
            found = False
            pass

        if not found:
            try:
                profileLink = self.driver.find_element(
                    By.CSS_SELECTOR, 'a.app-aware-link:has(span.jobs-poster__name)'
                )
                if profileLink and 'https://www.linkedin.com' in profileLink.get_attribute('href'):
                    found = True
                else:
                    found = False
            except:
                found = False
                pass

        if found:
            try:
                if profileLink and 'https://www.linkedin.com' in profileLink.get_attribute('href'):
                    if not self.check_and_update_profile_link_csv(
                            profileLink.get_attribute('href'), self.csv_link_profile_file):
                        profileurl = profileLink.get_attribute('href')
                        self.driver.get(profileurl)
                        self.connection_request_instance.find_follow_and_connect()
            except:
                pass

    def Continue_to_next_step(self):
        try:
            address = self.driver.find_element(
                By.XPATH, "/html/body/div[3]/div/div/div[2]/div/div[2]/form/div/div[1]/div[7]/div/div/div[1]/div/input")
            if address and address.get_attribute("type") == "text":
                address.send_keys(credentials.houseAddress)
        except:
            pass
        try:
            self.click_using_mouse_move(self.driver.find_element(
                By.CSS_SELECTOR, "button[aria-label='Continue to next step']"))
        except:
            pass

    def check_and_update_profile_link_csv(self, link, csv_filename):
        found = True
    # Check if the CSV file exists
        if not os.path.exists(csv_filename):
            # If the CSV file doesn't exist, create it with the header
            with open(csv_filename, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['Link'])

        # Check if the link already exists in the CSV file
        with open(csv_filename, 'r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)
            existing_links = set(row[0] for row in csv_reader)

        if link not in existing_links:
            # If the link doesn't exist, append it to the CSV file
            with open(csv_filename, 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([link])
                found = False
        else:
            found = True
        return found

    def check_and_update_job_link_csv(self, link, csv_filename, status):
        found = True
        # Check if the CSV file exists
        if not os.path.exists(csv_filename):
            # If the CSV file doesn't exist, create it with the header
            with open(csv_filename, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['Link', 'Status'])

        # Check if the link already exists in the CSV file
        with open(csv_filename, 'r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)
            existing_links = set(row[0] for row in csv_reader)

        if link not in existing_links:
            # If the link doesn't exist, append it to the CSV file with Status=False
            with open(csv_filename, 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([link, status])
                found = False
        else:
            found = True
        self.write_Job_Url(link)
        return found

    def click_using_mouse_move(self, element, isscript=0):
        location = element.location
        size = element.size
        # Calculate the coordinates of the center of the element
        x = location['x'] + size['width'] // 2
        y = location['y'] + size['height'] // 2
        try:
            pyautogui.moveTo(x, y, duration=random.uniform(.4, .8))
        except:
            pass

        if isscript == 0:
            # pyautogui.click()
            time.sleep(random.uniform(.3, .5))
            element.click()
        else:
            time.sleep(random.uniform(.3, .5))
            self.driver.execute_script(
                "arguments[0].click();", element)


start = time.time()
Linkedin().linkJobApply()
end = time.time()
utils.prYellow(
    "---Took: " + str(round((time.time() - start)/60)) + " minute(s).")
