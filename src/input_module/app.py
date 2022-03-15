from urllib.request import Request, urlopen
import shutil
import os
import docx
import uvicorn
from bs4 import BeautifulSoup
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Welcome to the input module!"

@app.post("/")


@app.post("/doc")
async def doc_input(file: UploadFile = File(...)):
    try:
        with open(f'{file.filename}', 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        filename = file.filename
        # path = os.path.realpath(__file__)
        path = os.getcwd()
        doc = docx.Document(str(path) + "\\" + filename)
        data = ""
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
            data = '\n'.join(fullText)

        os.remove(str(path) + "\\" + filename)
        return {'file content': data}

    except (Exception, IOError) as e:
        return {"exception": str(e)}


@app.post("/url")
async def url_input(url):
    req = Request(url)
    html_page = urlopen(req)

    soup = BeautifulSoup(html_page, "html.parser")

    html_text = soup.get_text()

    f = open("html_text.txt", "w", encoding='utf-8')  # Creating html_text.txt File

    for line in html_text:
        f.write(line)

    f.close()


@app.post("/pdf")
async def pdf_input(pdf):
    pass


@app.post("/txt")
async def txt_input(file: UploadFile = File(...)):
    try:
        data = file.file.read()
        return {'file content': data}

    except (Exception, IOError) as e:
        return {"exception": str(e)}


if __name__ == "__main__":
    # Run uvicorn server from inside docker
    uvicorn.run(app)
    # url_input("https://en.wikipedia.org/wiki/Python_(programming_language)")