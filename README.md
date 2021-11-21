<div align="center">
  <h1>discord-py-slash-components-bridge</h1>
  <h3>Bridge for discord-interactions and discord-components</h3>
</div>
<div align="center">
  <a href="https://pepy.tech/project/discord-slash-components-bridge"><img src="https://static.pepy.tech/personalized-badge/discord-slash-components-bridge?period=total&units=none&left_color=grey&right_color=blue&left_text=Downloads"></a>
  
</div>

<h2>Welcome</h2>
 
[discord-interactions](https://github.com/goverfl0w/discord-interactions) and [discord-components](https://github.com/kiki7000/discord.py-components) are incompatible and this bridge can compatible these libs.
This lib overrides discord-interaction classes and methods for working with discord-components components(Selects and Buttons)

<h2>Installing</h2>

`pip install --upgrade discord-slash-components-bridge`

<h2>How to use?</h2>

```py
from discord.ext import commands
#from discord_slash import SlashCommand # No need anymore
from discord_slash_components_bridge import SlashCommand

bot = commands.Bot(...)
slash = SlashCommand(bot, ...)

```
<h2>What have been fixed?</h2>

Fixed `Messageable.fetch_message()` returning `discord.Message`. Now it return `ComponentMessage`

<h2>Migration from discord-components</h2>
If you have used this, then I prepared for you some things.

- Now you no need `DiscordComponents(...)` in your code.
- Events `button_click` and `select_option` have been saved.
- Event `interaction` now is `component`.
- `Interaction` is not available to use. Now it's `ComponentContext` and now you need use methods of `ComponentContext`

<h2>If you used components of discord-py-interactions</h2>

- Now You can't use components of `discord-py-interactions`. You will get error.
- `ComponentContext.component` now return `Component` object(like `Button` or `Select`) from `discord-components` 
- with `ComponentContext.message.components` same thing.


<h2>Have some troubles?</h2>
Open issue is this repository or dm me in <a href="https://discordapp.com/users/%E2%80%8B143773579320754177">Discord</a>
