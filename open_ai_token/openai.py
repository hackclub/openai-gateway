from typing import Optional
from typing_extensions import Generator
import requests
from dotenv import load_dotenv
import os

from open_ai_token.schemas import Token, User
from open_ai_token.crud import get_token
from open_ai_token.database import SessionLocal
from open_ai_token.models import User as UserModel

db = SessionLocal()

load_dotenv()

# Request to OpenAI API to get the answer, basically act as an API gateway to OpenAI API

#* Models

def models():
    """
        Get the list of models available on OpenAI API
    """
    req = requests.get('https://api.openai.com/v1/models', headers={"Authorization": f"Bearer {os.getenv('OPEN_AI_KEY')}"})
    if req.status_code != 200:
        raise Exception(req.json())
    return req.json(), req.status_code, req.headers


def model(model_name):
    """
        Get the details of a model available on OpenAI API
    """
    req = requests.get(f'https://api.openai.com/v1/models/{model_name}', headers={"Authorization": f"Bearer {os.getenv('OPEN_AI_KEY')}"})
    if req.status_code != 200:
        raise Exception(req.json())
    return req.json(), req.status_code, req.headers

#* Chat

def post_chat_completions(data: dict, sec: Token):
    """
        Post a chat to OpenAI API
    """
    blocked_models=["gpt-4-turbo-preview","gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-4-1106-preview", "gpt-4-0613", "gpt-4o-2024-05-13"]

    usr: UserModel = get_token(db, sec.token)
    if data["model"] in blocked_models and not usr.user.gpt4_usage_allowed:
        return {"error": "This model is not available for use at this time."}, 403, {"error": "This model is not available for use at this time."}

    try:
        def gen():
            with requests.post('https://api.openai.com/v1/chat/completions', json=data, headers={"Authorization": f"Bearer {os.getenv('OPEN_AI_KEY')}"}, stream=True) as req:
                if req.status_code != 200:
                    raise Exception(req.json())
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
        with requests.post('https://api.openai.com/v1/images/generations', json=data, headers={"Authorization": f"Bearer {os.getenv('OPEN_AI_KEY')}"}, stream=True) as req:
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
        with requests.post('https://api.openai.com/v1/embeddings', json=data, headers={"Authorization": f"Bearer {os.getenv('OPEN_AI_KEY')}"}, stream=True) as req:
            for chunk in req.iter_content(chunk_size=1024):
                yield chunk
    except Exception as e:
        return {"error": str(e)}, 500, {"error": str(e)}


def create_fine_tuning(data):
    """
        Create a fine tuning on OpenAI API
    """
    try:
        with requests.post('https://api.openai.com/v1/fine_tuning/jobs', json=data, headers={"Authorization": f"Bearer {os.getenv('OPEN_AI_KEY')}"}, stream=True) as req:
            for chunk in req.iter_content(chunk_size=1024):
                yield chunk
    except Exception as e:
        return {"error": str(e)}, 500, {"error": str(e)}

def list_fine_tuning():
    """
        List all fine tuning on OpenAI API
    """
    try:
        with requests.get('https://api.openai.com/v1/fine_tuning/jobs', headers={"Authorization": f"Bearer {os.getenv('OPEN_AI_KEY')}"}, stream=True) as req:
            for chunk in req.iter_content(chunk_size=1024):
                yield chunk
    except Exception as e:
        return {"error": str(e)}, 500, {"error": str(e)}

def list_fine_tuning_events(job_id):
    """
        List all fine tuning events on OpenAI API
    """
    try:
        with requests.get(f'https://api.openai.com/v1/fine_tuning/jobs/{job_id}/events', headers={"Authorization": f"Bearer {os.getenv('OPEN_AI_KEY')}"}, stream=True) as req:
            for chunk in req.iter_content(chunk_size=1024):
                yield chunk
    except Exception as e:
        return {"error": str(e)}, 500, {"error": str(e)}

def list_fine_tuning_checkpoints(job_id):
    """
        List all fine tuning checkpoints on OpenAI API
    """
    try:
        with requests.get(f'https://api.openai.com/v1/fine_tuning/jobs/{job_id}/checkpoints', headers={"Authorization": f"Bearer {os.getenv('OPEN_AI_KEY')}"}, stream=True) as req:
            for chunk in req.iter_content(chunk_size=1024):
                yield chunk
    except Exception as e:
        return {"error": str(e)}, 500, {"error": str(e)}

def retrieve_fine_tuning(job_id):
    """
        Retrieve a fine tuning on OpenAI API
    """
    try:
        with requests.get(f'https://api.openai.com/v1/fine_tuning/jobs/{job_id}', headers={"Authorization": f"Bearer {os.getenv('OPEN_AI_KEY')}"}, stream=True) as req:
            for chunk in req.iter_content(chunk_size=1024):
                yield chunk

    except Exception as e:
        return {"error": str(e)}, 500, {"error": str(e)}

def cancel_fine_tuning(job_id):
    """
        Cancel a fine tuning on OpenAI API
    """
    try:
        with requests.post(f'https://api.openai.com/v1/fine_tuning/jobs/{job_id}/cancel', headers={"Authorization": f"Bearer {os.getenv('OPEN_AI_KEY')}"}, stream=True) as req:
            for chunk in req.iter_content(chunk_size=1024):
                yield chunk
    except Exception as e:
        return {"error": str(e)}, 500, {"error": str(e)}

# Batch Endpoints

def create_batch(data):
    """
        Create a batch on OpenAI API
    """
    try:
        with requests.post('https://api.openai.com/v1/batches', json=data, headers={"Authorization": f"Bearer {os.getenv('OPEN_AI_KEY')}"}, stream=True) as req:
            for chunk in req.iter_content(chunk_size=1024):
                yield chunk
    except Exception as e:
        return {"error": str(e)}, 500, {"error": str(e)}

def retrieve_batch(job_id):
    """
        Retrieve a batch on OpenAI API
    """
    try:
        with requests.get(f'https://api.openai.com/v1/batches/{job_id}', headers={"Authorization": f"Bearer {os.getenv('OPEN_AI_KEY')}"}, stream=True) as req:
            for chunk in req.iter_content(chunk_size=1024):
                yield chunk

    except Exception as e:
        return {"error": str(e)}, 500, {"error": str(e)}

def cancel_batch(job_id):
    """
        Cancel a batch on OpenAI API
    """
    try:
        with requests.post(f'https://api.openai.com/v1/batches/{job_id}/cancel', headers={"Authorization": f"Bearer {os.getenv('OPEN_AI_KEY')}"}, stream=True) as req:
            for chunk in req.iter_content(chunk_size=1024):
                yield chunk
    except Exception as e:
        return {"error": str(e)}, 500, {"error": str(e)}

def list_batches():
    """
        List all batches on OpenAI API
    """
    try:
        with requests.get('https://api.openai.com/v1/batches', headers={"Authorization": f"Bearer {os.getenv('OPEN_AI_KEY')}"}, stream=True) as req:
            for chunk in req.iter_content(chunk_size=1024):
                yield chunk
    except Exception as e:
        return {"error": str(e)}, 500, {"error": str(e)}
