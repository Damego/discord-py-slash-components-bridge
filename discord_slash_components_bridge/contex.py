from typing import List, Union

import discord
from discord.ext import commands
from discord_slash import error, http, model
from discord_slash.context import (
    InteractionContext,
    ComponentContext as _ComponentContext
    )
from discord_components import Component, ActionRow
from .utils import _get_components_json

from .dpy_overrides import ComponentMessage



async def ic_send(
    self,
    content: str = "",
    *,
    embed: discord.Embed = None,
    embeds: List[discord.Embed] = None,
    tts: bool = False,
    file: discord.File = None,
    files: List[discord.File] = None,
    allowed_mentions: discord.AllowedMentions = None,
    hidden: bool = False,
    delete_after: float = None,
    components: List[Union[ActionRow, Component, List[Component]]] = None,
) -> model.SlashMessage:
    """
    Sends response of the interaction.

    :param content:  Content of the response.
    :type content: str
    :param embed: Embed of the response.
    :type embed: discord.Embed
    :param embeds: Embeds of the response. Maximum 10.
    :type embeds: List[discord.Embed]
    :param tts: Whether to speak message using tts. Default ``False``.
    :type tts: bool
    :param file: File to send.
    :type file: discord.File
    :param files: Files to send.
    :type files: List[discord.File]
    :param allowed_mentions: AllowedMentions of the message.
    :type allowed_mentions: discord.AllowedMentions
    :param hidden: Whether the message is hidden, which means message content will only be seen to the author.
    :type hidden: bool
    :param delete_after: If provided, the number of seconds to wait in the background before deleting the message we just sent. If the deletion fails, then it is silently ignored.
    :type delete_after: float
    :param components: Message components in the response. The top level must be made of ActionRows.
    :type components: List[Union[ActionRow, Component, List[Component]]]
    :return: Union[discord.Message, dict]
    """
    if embed and embeds:
        raise error.IncorrectFormat("You can't use both `embed` and `embeds`!")
    if embed:
        embeds = [embed]
    if embeds:
        if not isinstance(embeds, list):
            raise error.IncorrectFormat("Provide a list of embeds.")
        elif len(embeds) > 10:
            raise error.IncorrectFormat("Do not provide more than 10 embeds.")
    if file and files:
        raise error.IncorrectFormat("You can't use both `file` and `files`!")
    if file:
        files = [file]
    if delete_after and hidden:
        raise error.IncorrectFormat("You can't delete a hidden message!")
    if components:
        components = _get_components_json(components)

    if allowed_mentions is not None:
        if self.bot.allowed_mentions is not None:
            allowed_mentions = self.bot.allowed_mentions.merge(allowed_mentions).to_dict()
        else:
            allowed_mentions = allowed_mentions.to_dict()
    else:
        if self.bot.allowed_mentions is not None:
            allowed_mentions = self.bot.allowed_mentions.to_dict()
        else:
            allowed_mentions = {}

    base = {
        "content": content,
        "tts": tts,
        "embeds": [x.to_dict() for x in embeds] if embeds else [],
        "allowed_mentions": allowed_mentions,
        "components": components or [],
    }
    if hidden:
        base["flags"] = 64

    initial_message = False
    if not self.responded:
        initial_message = True
        if files and not self.deferred:
            await self.defer(hidden=hidden)
        if self.deferred:
            if self._deferred_hidden != hidden:
                self._logger.warning(
                    "Deferred response might not be what you set it to! (hidden / visible) "
                    "This is because it was deferred in a different state."
                )
            resp = await self._http.edit(base, self._token, files=files)
            self.deferred = False
        else:
            json_data = {"type": 4, "data": base}
            await self._http.post_initial_response(json_data, self.interaction_id, self._token)
            if not hidden:
                resp = await self._http.edit({}, self._token)
            else:
                resp = {}
        self.responded = True
    else:
        resp = await self._http.post_followup(base, self._token, files=files)
    if files:
        for file in files:
            file.close()
    if not hidden:
        smsg = model.SlashMessage(
            state=self.bot._connection,
            data=resp,
            channel=self.channel or discord.Object(id=self.channel_id),
            _http=self._http,
            interaction_token=self._token,
        )
        if delete_after:
            self.bot.loop.create_task(smsg.delete(delay=delete_after))
        if initial_message:
            self.message = smsg
        return smsg
    else:
        return resp

InteractionContext.send = ic_send

class ComponentContext(_ComponentContext):
    def __init__(
        self,
        _http: http.SlashCommandRequest,
        _json: dict, _discord:
        Union[discord.Client, commands.Bot],
        logger
        ):
        self.custom_id = self.component_id = _json["data"]["custom_id"]
        self.component_type = _json["data"]["component_type"]
        super().__init__(_http=_http, _json=_json, _discord=_discord, logger=logger)
        self.origin_message = None
        self.origin_message_id = int(_json["message"]["id"]) if "message" in _json.keys() else None

        self.component = None

        self._deferred_edit_origin = False

        if self.origin_message_id and (_json["message"]["flags"] & 64) != 64:
            self.origin_message = ComponentMessage(
                state=self.bot._connection, channel=self.channel, data=_json["message"]
            )
            self.message = self.origin_message
            self.component = self.message.get_component(self.custom_id)

        self.selected_options = None

        if self.component_type == 3:
            self.selected_options = _json["data"].get("values", [])

    async def edit_origin(self, **fields):
        """
        Edits the origin message of the component.
        Refer to :meth:`discord.Message.edit` and :meth:`InteractionContext.send` for fields.
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
                _resp["components"] =  _get_components_json(components)

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
            if self.bot.allowed_mentions is not None:
                _resp["allowed_mentions"] = self.bot.allowed_mentions.merge(
                    allowed_mentions
                ).to_dict()
            else:
                _resp["allowed_mentions"] = allowed_mentions.to_dict()
        else:
            if self.bot.allowed_mentions is not None:
                _resp["allowed_mentions"] = self.bot.allowed_mentions.to_dict()
            else:
                _resp["allowed_mentions"] = {}

        if not self.responded:
            if files and not self.deferred:
                await self.defer(edit_origin=True)
            if self.deferred:
                if not self._deferred_edit_origin:
                    self._logger.warning(
                        "Deferred response might not be what you set it to! (edit origin / send response message) "
                        "This is because it was deferred with different response type."
                    )
                _json = await self._http.edit(_resp, self._token, files=files)
                self.deferred = False
            else:  # noqa: F841
                json_data = {"type": 7, "data": _resp}
                _json = await self._http.post_initial_response(  # noqa: F841
                    json_data, self.interaction_id, self._token
                )
            self.responded = True
        else:
            raise error.IncorrectFormat("Already responded")

        if files:
            for file in files:
                file.close()