from selenium import webdriver
# Import the ConnectionRequest class
from connection_request import ConnectionRequest
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


class AnotherClass:
    def __init__(self):
        self.today_date = datetime.today().strftime('%Y%m%d')
        self.driver = webdriver.Chrome(service=ChromeService(
            ChromeDriverManager().install()), options=utils.chromeBrowserOptions())


def read_questions_and_answers(FieldType):
    # FieldType TextBox=1,Radio=2,Dropdown=3
    try:
        All_data = pd.read_csv('Q_A_File', encoding='utf-8',
                               na_values=['None'])
        data = All_data[All_data['FieldType'] == FieldType]
        question_answer_tuples = list(zip(data['Question'].tolist(
        ), data['Answer'].tolist(), data['FieldType'].tolist()))
        questions_and_answers = dict((question, {'Answer': answer, 'FieldType': fieldType})
                                     for question, answer, fieldType in question_answer_tuples)
        return questions_and_answers
    except Exception as e:
        print(e)
        return {}


def read_questions_and_answers_GroupBy():
    try:
        All_data = pd.read_csv('Q_A_File', encoding='utf-8',
                               na_values=['None'])
        data = All_data[All_data['FieldType'] == 3]
        grouped_data = data.groupby('Question').agg({
            'Answer': list,
            'FieldType': 'first'
        }).reset_index()
        questions_and_answers = dict(zip(grouped_data['Question'], zip(
            grouped_data['Answer'], grouped_data['FieldType'])))
        return questions_and_answers
    except Exception as e:
        print(e)
        return {}


def answer_Not_Found(question, FieldType, question_element=None):
    lang = detect(question)
    if lang != 'en':
        translator = Translator()
        translation = translator.translate(question, dest='en')
        translated_word = translation.text
    else:
        # If the language is already English, use the original question
        translated_word = question

    questionText = 'Question in English\n' + translated_word
    if translated_word != question:
        questionText = questionText + '\nQuestion in Other Language\n' + question
    _input = questionText + '\n'
    user_input = input(f"\033[92m{_input}\033[00m")
    processed_output = f"{user_input}"

    separated_values = processed_output.split(',')

    finalQuestion = separated_values[0]
    finalAns = separated_values[1]
    existing_df = pd.read_csv(
        'Q_A_File', encoding='utf-8', na_values=['None'])
    new_data = {'Question': [finalQuestion], 'Answer': [
        finalAns], 'FieldType': [FieldType]}
    new_df = pd.DataFrame(new_data)
    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    # Corrected file extension to '.csv'
    updated_df.to_csv('Q_A_File', index=False)


# Example usage
if __name__ == "__main__":
    questions_and_answers1 = read_questions_and_answers(1)
    if 'C++' in questions_and_answers1:
        print(questions_and_answers1['C++']['Answer'])
    else:
        print('false')
    questions_and_answers2 = read_questions_and_answers(2)

    for question_csv_kay, element in questions_and_answers2.items():
        split_ans = question_csv_kay.split('-')
        if all(part in 'What are your salary expectations please?' for part in split_ans):
            matching_element = element['Answer']
            print(matching_element)
            break
        else:
            print('false')

    questions_and_answers = read_questions_and_answers_GroupBy()

    answer_Not_Found("Are you single", 2)
