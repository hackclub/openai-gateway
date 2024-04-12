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

    if bypass_gpt4_restriction and "model" in json_data:
        if any([x in json_data["model"] for x in ["gpt-4", "gpt-4-turbo"]] + ["gpt-4" in json_data["model"][:5], "gpt-4-turbo" in json_data["model"][:11]]):
            raise ValueError("You are not allowed to use GPT-4 or GPT-4 Turbo Preview")

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions", json=json_data, headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status

async def embeddings(json_data):
    """
    This function sends a POST request to the OpenAI API to get embeddings
    :param json_data: The JSON data to be sent to the API
    """

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/embeddings", json=json_data, headers={"Authorization": f"Bearer {OPEN_AI_TOKEN_ORG}"} ) as response:
            # return response json and status code
            return await response.json(), response.status
