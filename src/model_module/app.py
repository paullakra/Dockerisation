from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn
from pydantic import BaseModel

from src.model_module import generate_summary


class TextInput(BaseModel):
    unix_time: int
    text: str
    user_id: int
    hash_value: int = hash(text)


app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
def root():
    return "Welcome to the model module!"


@app.post("/input/", response_class=PlainTextResponse)
def get_summary(text_wrapper: TextInput):
    temp = generate_summary(text_wrapper.text)
    # send inference to database instead of user
    return temp


if __name__ == "__main__":
    # Run uvicorn server from inside docker
    uvicorn.run(app)

