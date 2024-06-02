from typing import Optional
from typing_extensions import Generator
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Request to OpenAI API to get the answer, basically act as an API gateway to OpenAI API

#* Models

def models():
    """
        Get the list of models available on OpenAI API
    """
    req = requests.get('https://api.openai.com/v1/models', headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"})
    if req.status_code != 200:
        raise Exception(req.json())
    return req.json(), req.status_code, req.headers


def model(model_name):
    """
        Get the details of a model available on OpenAI API
    """
    req = requests.get(f'https://api.openai.com/v1/models/{model_name}', headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"})
    if req.status_code != 200:
        raise Exception(req.json())
    return req.json(), req.status_code, req.headers

#* Chat

def post_chat_completions(data):
    """
        Post a chat to OpenAI API
    """
    blocked_models=["gpt-4-turbo-preview", "gpt-4"]
    if data["model"] in blocked_models:
        return {"error": "This model is not available for use at this time."}, 403, {"error": "This model is not available for use at this time."}

    try:
        def gen():
            with requests.post('https://api.openai.com/v1/chat/completions', json=data, headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}, stream=True) as req:
                for chunk in req.iter_content(chunk_size=1024):
                    yield chunk
        return gen()

    except Exception as e:
        return {"error": str(e)}, 500, {"error": str(e)}

#* Image

def create_image(data):
    """
        Create an image on OpenAI API
    """
    try:
        with requests.post('https://api.openai.com/v1/images/generations', json=data, headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}, stream=True) as req:
            for chunk in req.iter_content(chunk_size=1024):
                yield chunk
    except Exception as e:
        return {"error": str(e)}, 500, {"error": str(e)}

    # Todo: Add more endpoints that are available on OpenAI API, particularly which require file upload

#* Embeddings

def embeddings(data):
    """
        Get the embeddings of a text on OpenAI API
    """
    try:
        with requests.post('https://api.openai.com/v1/embeddings', json=data, headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}, stream=True) as req:
            for chunk in req.iter_content(chunk_size=1024):
                yield chunk
    except Exception as e:
        return {"error": str(e)}, 500, {"error": str(e)}

#* Files

#TODO: Add file upload endpoints

#* Audio

#TODO: Add audio endpoints
