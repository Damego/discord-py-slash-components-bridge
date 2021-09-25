from discord_slash import SlashCommand as _SlashCommand
from discord_components import InteractionEventType, Component

from .contex import ComponentContext


class SlashCommand(_SlashCommand):
    _components_callback = {}
    async def _on_component(self, to_use):
        ctx = ComponentContext(self.req, to_use, self._discord, self.logger)
        self._discord.dispatch("component", ctx)

        if self._components_callback.get(ctx.custom_id):
            callback_info = self._components_callback[ctx.custom_id]
            if callback_info["uses"] == 0:
                del self._components_callback[ctx.custom_id]
                return

            if callback_info["uses"] is not None:
                self._components_callback[ctx.custom_id]["uses"] -= 1
            if not callback_info["filter"](ctx):
                return

            await self._components_callback[ctx.custom_id]["callback"](ctx)

        for _type in InteractionEventType:
            if _type.value == to_use["data"]["component_type"]:
                self._discord.dispatch(f"raw_{_type.name}", to_use)
                self._discord.dispatch(_type.name, ctx)
                break

    def add_callback(self, component: Component, callback, *, uses: int = None, filter=None):
        self._components_callback[component.custom_id] = {
            "callback": callback,
            "uses": uses,
            "filter": filter or (lambda x: True),
        }
        return component

