from typing import Literal

import discord
import requests
from requests.structures import CaseInsensitiveDict

from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]


class openai(commands.Cog):
    """
    Makes calls to the OpenAI API.
    """

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=933515020313178152,
            force_registration=True,
        )

