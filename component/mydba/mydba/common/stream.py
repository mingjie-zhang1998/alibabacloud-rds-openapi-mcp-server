# -*- coding: utf-8 -*-
from prompt_toolkit import PromptSession
import asyncio

async def ainput(prompt=""):
    session = PromptSession()
    input = await asyncio.to_thread(session.prompt, prompt)
    return input.rstrip("\n")

async def aprint(*values):
    print(*values, flush=True)
