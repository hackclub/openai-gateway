import aiohttp
import asyncio
from dotenv import load_dotenv

import os

load_dotenv()

OPEN_AI_TOKEN_ORG = os.getenv("OPEN_AI_KEY")

if OPEN_AI_TOKEN_ORG is None:
    raise ValueError("OPEN_AI_TOKEN_ORG is not set")

async def chat_completions(json_data, bypass_gpt4_restriction=False):
    """
    This function sends a POST request to the OpenAI API to get chat completions
    :param json_data: The JSON data to be sent to the API
    :param bypass_gpt4_restriction: Whether to bypass the GPT-4 restriction, defaults to False
    """

    #validating the json data
    if "model" not in json_data:
        raise ValueError("Model not found in JSON data")
    if "messages" not in json_data:
        raise ValueError("Messages not found in JSON data")
    if "frequency_penalty" in json_data and (json_data["frequency_penalty"] < -2.0 or json_data["frequency_penalty"] > 2.0):
        raise ValueError("Frequency Penalty must be between -2.0 and 2.0")
    if "logit_bias" in json_data and (json_data["logit_bias"] < -100.0 or json_data["logit_bias"] > 100.0):
        raise ValueError("Logit Bias must be between -100.0 and 100.0")
    if "top_logprobs" in json_data and (json_data["top_logprobs"] < 0 or json_data["top_logprobs"] > 20):
        raise ValueError("Top Logprobs must be between 0 and 20")


    if bypass_gpt4_restriction and "model" in json_data:
        if any([x in json_data["model"] for x in ["gpt-4", "gpt-4-turbo"]] + ["gpt-4" in json_data["model"][:5], "gpt-4-turbo" in json_data["model"][:11]]):
            raise ValueError("You are not allowed to use GPT-4 or GPT-4 Turbo Preview")

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions", json=json_data, headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # yield response json and status code
            for chunk in response.content.iter_any():
                yield chunk

async def embeddings(json_data):
    """
    This function sends a POST request to the OpenAI API to get embeddings
    :param json_data: The JSON data to be sent to the API
    """

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/embeddings", json=json_data, headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def fine_tuning_post(json_data):
    """
    This function sends a POST request to the OpenAI API to fine tune a model
    :param json_data: The JSON data to be sent to the API
    """

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/fine_tuning/jobs", json=json_data, headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def fine_tuning_get(params):
    """
    This function sends a GET request to the OpenAI API to get the status of a fine tuning job
    :param params: The parameters to be sent to the API
    """

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.openai.com/v1/fine_tuning/jobs", params=params, headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def fine_tuning_list_events(job_id, params):
    """
    This function sends a GET request to the OpenAI API to list events of a fine tuning job
    :param job_id: The job ID of the fine tuning job
    :param params: The parameters to be sent to the API
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.openai.com/v1/fine_tuning/jobs/{job_id}/events", params=params, headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def fine_tuning_list_checkpoints(job_id, params):
    """
    This function sends a GET request to the OpenAI API to list checkpoints of a fine tuning job
    :param job_id: The job ID of the fine tuning job
    :param params: The parameters to be sent to the API
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.openai.com/v1/fine_tuning/jobs/{job_id}/checkpoints", params=params, headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def retrieve_fine_tuning_jobs(job_id):
    """
    This function sends a GET request to the OpenAI API to retrieve a fine tuning job
    :param job_id: The job ID of the fine tuning job
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.openai.com/v1/fine_tuning/jobs/{job_id}", headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def cancel_fine_tuning_job(job_id):
    """
    This function sends a POST request to the OpenAI API to cancel a fine tuning job
    :param job_id: The job ID of the fine tuning job
    """

    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://api.openai.com/v1/fine_tuning/jobs/{job_id}/cancel", headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def batches(json_data):
    """
    This function sends a POST request to the OpenAI API to create a batch
    :param json_data: The JSON data to be sent to the API
    """

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/batches", json=json_data, headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def retrieve_batches(batch_id):
    """
    This function sends a GET request to the OpenAI API to retrieve a batch
    :param batch_id: The batch ID of the batch
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.openai.com/v1/batches/{batch_id}", headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def cancel_batch(batch_id):
    """
    This function sends a POST request to the OpenAI API to cancel a batch
    :param batch_id: The batch ID of the batch
    """

    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://api.openai.com/v1/batches/{batch_id}/cancel", headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def list_batches(params):
    """
    This function sends a GET request to the OpenAI API to list batches
    :param params: The parameters to be sent to the API
    """

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.openai.com/v1/batches", params=params, headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def upload_file(file_path, purpose):
    """
    This function sends a POST request to the OpenAI API to upload a file
    :param file_path: The path of the file to be uploaded
    :param purpose: The purpose of the file
    """

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/files", data={"purpose": purpose}, files={"file": open(file_path, "rb")} , headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def list_files(params):
    """
    This function sends a GET request to the OpenAI API to list files
    :param params: The parameters to be sent to the API
    """

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.openai.com/v1/files", params=params, headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def retrieve_file(file_id):
    """
    This function sends a GET request to the OpenAI API to retrieve a file
    :param file_id: The file ID of the file
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.openai.com/v1/files/{file_id}", headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def delete_file(file_id):
    """
    This function sends a DELETE request to the OpenAI API to delete a file
    :param file_id: The file ID of the file
    """

    async with aiohttp.ClientSession() as session:
        async with session.delete(f"https://api.openai.com/v1/files/{file_id}", headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def retrieve_file_content(file_id):
    """
    This function sends a GET request to the OpenAI API to retrieve the contents of a file
    :param file_id: The file ID of the file
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.openai.com/v1/files/{file_id}/content", headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def image_generation(json_data):
    """
    This function sends a POST request to the OpenAI API to generate an image
    :param json_data: The JSON data to be sent to the API
    """

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/images/generations", json=json_data, headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def edit_image_generation(json_data):
    """
    This function sends a POST request to the OpenAI API to edit an image
    :param json_data: The JSON data to be sent to the API
    """

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/images/edits", json=json_data, headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def create_image_variation(json_data, image):
    """
    This function sends a POST request to the OpenAI API to create an image variation
    :param json_data: The JSON data to be sent to the API
    :param image: The image to be uploaded
    """

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/images/variations", json=json_data, files={"image": open(image, "rb")}, headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status
