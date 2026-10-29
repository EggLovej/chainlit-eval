"""Minimal Chainlit chat against OpenRouter, used for the chat framework evaluation.

Env:
    OPENROUTER_API_KEY  required
    CHAINLIT_MODELS     comma-separated OpenRouter model ids; the first is the default
"""

import os

from openai import AsyncOpenAI

import chainlit as cl
from chainlit.input_widget import Select

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
MODELS = [
    m.strip()
    for m in os.environ.get("CHAINLIT_MODELS", "openai/gpt-4o-mini").split(",")
    if m.strip()
]


@cl.on_chat_start
async def on_chat_start():
    settings = await cl.ChatSettings(
        [Select(id="model", label="Model", values=MODELS, initial_index=0)]
    ).send()
    cl.user_session.set("model", settings["model"])
    cl.user_session.set("history", [])


@cl.on_settings_update
async def on_settings_update(settings):
    cl.user_session.set("model", settings["model"])


@cl.on_message
async def on_message(message: cl.Message):
    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

    reply = cl.Message(content="")
    stream = await client.chat.completions.create(
        model=cl.user_session.get("model"), messages=history, stream=True
    )
    async for chunk in stream:
        if chunk.choices and (token := chunk.choices[0].delta.content):
            await reply.stream_token(token)
    await reply.send()

    history.append({"role": "assistant", "content": reply.content})
