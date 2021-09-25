<div align="center">
  <h1>discord-py-slash-components-bridge</h1></div>
  <h3>Bridge for discord-interaction and discord-components</h3>
  
 
<h2>Welcome</h2>
 
[discord-interaction](https://github.com/goverfl0w/discord-interactions) and [discord-components](https://github.com/kiki7000/discord.py-components) are incompatible and this bridge can compatible these libs.
This lib overrides discord-interaction classes and methods for working with discord-components components(Selects and Buttons)

<h2>How to use?</h2>
```py
#from discord_slash import SlashCommand #
from discord_py_slash_bridge import SlashCommand()

bot = <commands.Bot>(...)
slash = SlashCommand(...)
```
