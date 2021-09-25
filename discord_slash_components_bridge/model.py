import asyncio
from contextlib import suppress

import discord
from discord_slash import http, error

from .dpy_overrides import ComponentMessage, _get_components_json


class SlashMessage(ComponentMessage):
    """discord.py's :class:`discord.Message` but overridden ``edit`` and ``delete`` to work for slash command."""

    def __init__(self, *, state, channel, data, _http: http.SlashCommandRequest, interaction_token):
        # Yes I know it isn't the best way but this makes implementation simple.
        super().__init__(state=state, channel=channel, data=data)
        self._http = _http
        self.__interaction_token = interaction_token

    async def _slash_edit(self, **fields):
        """
        An internal function
        """
        _resp = {}

        try:
            content = fields["content"]
        except KeyError:
            pass
        else:
            if content is not None:
                content = str(content)
            _resp["content"] = content

        try:
            components = fields["components"]
        except KeyError:
            pass
        else:
            if components is None:
                _resp["components"] = []
            else:
                _resp["components"] = _get_components_json(components)

        try:
            embeds = fields["embeds"]
        except KeyError:
            # Nope
            pass
        else:
            if not isinstance(embeds, list):
                raise error.IncorrectFormat("Provide a list of embeds.")
            if len(embeds) > 10:
                raise error.IncorrectFormat("Do not provide more than 10 embeds.")
            _resp["embeds"] = [e.to_dict() for e in embeds]

        try:
            embed = fields["embed"]
        except KeyError:
            pass
        else:
            if "embeds" in _resp:
                raise error.IncorrectFormat("You can't use both `embed` and `embeds`!")

            if embed is None:
                _resp["embeds"] = []
            else:
                _resp["embeds"] = [embed.to_dict()]

        file = fields.get("file")
        files = fields.get("files")

        if files is not None and file is not None:
            raise error.IncorrectFormat("You can't use both `file` and `files`!")
        if file:
            files = [file]

        allowed_mentions = fields.get("allowed_mentions")
        if allowed_mentions is not None:
            if self._state.allowed_mentions is not None:
                _resp["allowed_mentions"] = self._state.allowed_mentions.merge(
                    allowed_mentions
                ).to_dict()
            else:
                _resp["allowed_mentions"] = allowed_mentions.to_dict()
        else:
            if self._state.allowed_mentions is not None:
                _resp["allowed_mentions"] = self._state.allowed_mentions.to_dict()
            else:
                _resp["allowed_mentions"] = {}

        await self._http.edit(_resp, self.__interaction_token, self.id, files=files)

        delete_after = fields.get("delete_after")
        if delete_after:
            await self.delete(delay=delete_after)
        if files:
            [x.close() for x in files]

    async def edit(self, **fields):
        """Refer :meth:`discord.Message.edit`."""
        if "file" in fields or "files" in fields or "embeds" in fields or "components" in fields:
            await self._slash_edit(**fields)
        else:
            try:
                await super().edit(**fields)
            except discord.Forbidden:
                await self._slash_edit(**fields)

    async def delete(self, *, delay=None):
        """Refer :meth:`discord.Message.delete`."""
        try:
            await super().delete(delay=delay)
        except discord.Forbidden:
            if not delay:
                return await self._http.delete(self.__interaction_token, self.id)

            async def wrap():
                with suppress(discord.HTTPException):
                    await asyncio.sleep(delay)
                    await self._http.delete(self.__interaction_token, self.id)

            self._state.loop.create_task(wrap())
