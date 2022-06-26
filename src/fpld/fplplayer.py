from __future__ import annotations
from .team import fplteam
import fpl
from .util import API
import asyncio
import aiohttp


class FPLPlayer:
    def __init__(self, user_id: int):
        asyncio.run(self.foo(user_id))

    async def foo(self, user_id):
        async with aiohttp.ClientSession() as session:
            fpl_ = fpl.FPL(session)
            self.x = await fpl_.get_user(user_id)
