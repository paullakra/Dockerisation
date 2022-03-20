import os.path
import re
import chardet


def identify_file_type(file_path: str):
    print("damn")
    # Function to identify type of file
    try:
        if os.path.isdir(file_path):
            return {"file_type": "directory"}
        extension = file_path[file_path.rindex(".") + 1:]
        if extension.isalnum():
            return {"file_type": extension}
        else:
            return {"file_type": "unknown"}

    except ValueError as e:
        return {"file_type": "unknown", "error": e}


def identify_text_encoding(text):
    # Function to identify encoding of
    result = chardet.detect(text)
    char_enc = result['encoding']
    return {'encoding': char_enc}


def preprocess_string(text: str):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9. ]", "", text)
    return text


if __name__ == "__main__":
    print(identify_file_type(r"C:\Users\ppaul\.conda\envs\model_docker\lib\code.py"))
