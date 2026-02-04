# Documentation for extension system (written by blaze :>)

## To create a extension
- open extension.json file
- put the json exactly in this format
```json
{
  "test": {
    "id": "test",
    "title": "Test Extension",
    "description": "blah blah blah",
    "creator": "Blaze",
    "image": "https://cdn.discordapp.com/attachments/1351366618743181352/1464856068063760540/Picsart_26-01-25_11-04-27-721.png",
    "commands": [
      "test",
      "ping",
      "hello"
    ],
    "versions": {
      "1.0.0": "test.py",
      "2.0.0": "test2.py"
    }
  }
}
```


- the first **"test":** is the json object key, it should be same value as id 
- id is the value which will be used in installation of extension (extension install {id})

### rules for writing id
- no spaces
- no special characters (underscores are allowed)
- only alphabet and digits are allowed
- the id should be unique to avoid conflict with other extension


- title's is just title, the name of extension. There's no specific rules for it 
- description's contain the description (wow what an amazing sentance), there's no rule for it either
- creator contains your name
- image should ONLY contain discord cdn images
- commands should contain the exact names of commands present in extension
- the version part, this should contain the version and its corresponding file name
### rules/notes for version
- the version value should have the exact file name which contains that version of extension
- version added in bottom is treated as latest version (in the above example, version 2.0.0 will be treated as latest)
- you have to make a seperate file for each version so the users will have access to older versions of your extension
- to remove a version, delete its entry from the json
- you only have to specify the file name, not the entire path (**all extension's py file should be present in extensions folder ONLY**)

## Notes to remember before panicking
- extension's library/data is automatically updated every 1hr
- extension's data is only fetched from the main branch
- I have made 2 extensions which you can read to understand the fundamentals

## code style
```py
from discord.ext import commands


class testey(commands.Cog):  # having class is necessary
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="hi", description="says hi")
    async def hi(self, ctx):
        await ctx.send("hi")


async def setup(bot):
    await bot.add_cog(testey(bot))
```
- you always have to register commands inside a class
- you do **NOT** have to use ```bot``` decorator, you **MUST** have to use the ```commands``` decorator instead
- you **DO NOT** have to write bot.run or something like that, just add 
```py
async def setup(bot):
    await bot.add_cog(samevalueasclass(bot))
``` in the end
- you **DO NOT** have to define intents in extensions file, intents only belong to index.py file
- you **DO NOT** have to use 
```
@bot.events
``` use 
```
@commands.Cog.listener()
``` instead
- if you want to add a global variable to work all over bot, define the variable in index.py file else if you want to define a global variable only inside your extension then you have to use it like
```
 self.gg = gg
``` (I mean its a basic knowledge)
- you **DO NOT** have to define bot, prefixes or any such perameters in extensions since they belong to index.py **ONLY**
- you should always check the names of commands you are going to add so there should not be same command somewhere else in the bot 

## If you have any problems/question about extensions, dm [Blaze](https://discord.com/users/1238444724386533417)
