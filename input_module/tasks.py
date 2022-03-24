import chardet
import os
import re
import fitz
import requests
import time
import hashlib

import docx as python_docx

from .worker import celery_app
from database_module.utils import PostgreSQLWrapper


def doc(path):
    input = python_docx.Document(path)
    data = ""
    full_text = []
    for para in input.paragraphs:
        full_text.append(para.text)
        data = '\n'.join(full_text)

    return data


docx = doc


def txt(path):
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    return data


def pdf(path):
    fitz_doc = fitz.open(path)  # open document
    data = ""

    for page in fitz_doc:
        data = data + " " + page.get_text("text")

    return data


def identify_file_type(file_path: str):
    # Function to identify type of file
    try:
        if os.path.isdir(file_path):
            return "directory"
        extension = file_path[file_path.rindex(".") + 1:]
        if extension.isalnum():
            return extension
        else:
            return "unknown"

    except ValueError as e:
        return e


def preprocess_string(text: str):
    text = text.lower()
    # s = text.maketrans("\n\t\r\t\\", "     ")
    # text = text.translate(s)
    text = re.sub('\n', ' ', text)
    text = re.sub(r"[^a-zA-Z0-9. ]", "", text)
    text = re.sub(' +', ' ', text)
    text.strip()
    return text


def identify_text_encoding(text):
    # Function to identify encoding of given text body
    result = chardet.detect(text)
    char_enc = result['encoding']
    return {'encoding': char_enc}


@celery_app.task()
def get_prediction_update_db(file_path):
    now = time.time()
    db_wrapper = PostgreSQLWrapper("../database_module/sql_config.json")
    try:
        file_extension = identify_file_type(file_path)
        # text = exec("{}.delay('{}')".format(file_extension, file_path))
        if file_extension == "txt":
            text = txt(file_path)
        elif file_extension == "pdf":
            text = pdf(file_path)
        elif file_extension == "doc":
            text = doc(file_path)
        elif file_extension == "docx":
            text = docx(file_path)
        else:
            pass
        text = preprocess_string(text)
        hashed_text = hashlib.md5(text.encode('utf-8')).hexdigest()
        response = requests.post(url="http://127.0.0.1:5000/input", json={"text": text})
        task_id = celery_app.Task.__name__

        db_wrapper.check_connection(establish=True)
        db_wrapper.add_row("call_history", ["hash_value", "user_id", "unix_timestamp"],
                           [str(hashed_text), str(task_id), str(now)])

        return response.content.decode("utf-8")

    except Exception as e:
        return {"Error": str(e)}


if __name__ == "__main__":
    teg = "hjb7n89tg86nf976fb78t\h\n\t\r herthwt  sfdgvbnwrtywy4"
    path = "../database_module/sql_config.json"
    print(preprocess_string(teg))
