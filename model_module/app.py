from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn
from pydantic import BaseModel, validator

from transformers import BertTokenizerFast, EncoderDecoderModel
import torch


class TextInput(BaseModel):
    text: str


def load_model():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer = BertTokenizerFast.from_pretrained(
        'mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization')
    model = EncoderDecoderModel.from_pretrained(
        'mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization').to(
        device)
    return tokenizer, model, device


def generate_summary(text):
    # cut off at BERT max length 512
    tokenizer, model, device = load_model()
    inputs = tokenizer([text], padding="max_length", truncation=True, max_length=512, return_tensors="pt")
    input_ids = inputs.input_ids.to(device)
    attention_mask = inputs.attention_mask.to(device)

    output = model.generate(input_ids, attention_mask=attention_mask)

    return tokenizer.decode(output[0], skip_special_tokens=True)


app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
def root():
    return "Welcome to the model module!"


@app.post("/input", response_class=PlainTextResponse)
def get_summary(text_wrapper: TextInput):
    # TODO: send inference to database instead of user
    return generate_summary(text_wrapper.text)


if __name__ == "__main__":
    # Run uvicorn server from inside docker
    uvicorn.run(app, host="0.0.0.0", port=5000)
    # uvicorn.run(app)
