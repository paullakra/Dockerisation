from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, PlainTextResponse
import os
import shutil
from urllib.request import Request, urlopen
from celery.result import AsyncResult
import uvicorn
from bs4 import BeautifulSoup

from input_module.tasks import get_prediction_update_db
from database_module.utils import PostgreSQLWrapper

global db_wrapper
db_wrapper = PostgreSQLWrapper()
app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Welcome to the input module!"


@app.post("/file")
async def file_input(file: UploadFile = File(...)):
    try:
        with open(f'{file.filename}', 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_path = str(os.getcwd()) + "\\" + file.filename
        file_path = file_path.replace("\\", "/")
        celery_response = get_prediction_update_db.delay(file_path)
        # celery_response = get_prediction_update_db(file_path)
        response = JSONResponse(status_code=202, content=dict(ID=celery_response.id,
                                                              Message="The task is being executed. Please use the ID provided to check the status."))

    except RuntimeError as e:
        response = JSONResponse(status_code=400, content=dict(message=e))

    os.remove(file_path)
    return response


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


@app.get("/status/{task_id}", response_class=JSONResponse)
async def task_result(task_id):
    task = AsyncResult(task_id)
    if not task.ready():
        print(app.url_path_for('status'))
        return JSONResponse(status_code=202, content={'task_id': str(task_id), 'status': 'Processing'})
    result = task.get()
    return {'task_id': task_id, 'status': 'Success', 'message': str(result)}


if __name__ == "__main__":
    # Run uvicorn server from inside docker
    uvicorn.run(app, host="localhost", port=8000)
