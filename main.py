from discord.ext import commands
import discord, random, sys, requests, urllib, json, re, extensions, hashlib

tokenFile = json.load(open("auth.json", "r"))
token = tokenFile["bot"]

questionList = []
insultList = []
characterLimit = 1800
inspireToken = requests.get("https://inspirobot.me/api?getSessionID=1").text
database = extensions.serverInfo()

with open("questions.txt", "r") as qFile :
    questionList = qFile.readlines()

with open("insults.txt", "r") as iFile :
    insultList = iFile.readlines()

# Load all the data we need

bot = commands.Bot(command_prefix='/')

bot.remove_command("help") # We're over riding this with our own

# - - - All event handlers that are not on message go here - - -

@bot.event
async def on_ready():
    print('Logged on as', bot.user, flush=True)

# - - - All extra functions go here - - -

@bot.check
async def globally_block_dms(ctx): # This blocks all commmands that are not a DM
    return ctx.guild is not None

def permitted(ctx) : # This is to check if we can run the API functions in the server
    return database.checkServer(ctx.message)

# - - - Commands go here - - -
@bot.command()
async def ask(ctx) :
    gameActive = database.gameInProgress(ctx.message)
    if gameActive : 
        await ctx.channel.send("Oops! Looks like you already have a question active in this channel which is : *" + 
        gameActive + 
        "*\n\nYou will have to say `Goodbye` and then ask again if you would like another question!")

    else :
        question = random.choice(questionList).rstrip()
        database.startGame(question, ctx.message)
        await ctx.channel.send('Alright! Your statement is\n\n *' + question + '*\n\nRemember to say "Goodbye" once you are done!')

@bot.command()
@commands.has_permissions(manage_guild=True)
async def mode(ctx) :
    if permitted(ctx) : # If the server allows these, add it to the restricted list
        database.addServer(ctx.message)
        await ctx.channel.send("**API functions now disabled in this server**")

    else :
        database.removeServer(ctx.message) # If not, remove it
        await ctx.channel.send("**API functions now enabled in this server**")

@bot.command()
@commands.check(permitted)
async def inspire(ctx) :
    quoteJson = requests.get("https://inspirobot.me/api?generateFlow=1&sessionID=" + urllib.parse.quote(inspireToken, safe='')).text
    data = json.loads(quoteJson)
    quotes = "*" #Star for markdown

    for quote in data["data"] :
        try :
            quotes += re.sub("\[pause \d\][ \.]{0,}",".\n  ",quote["text"])
            quotes += "\n\n"
        except KeyError :
            pass

    quotes = quotes.rstrip() + "*" #Remove newlines so markdown still works
    await ctx.channel.send("AI, inspire us!\n\n" + quotes)
    print(hashlib.md5(str(ctx.guild.id).encode('utf-8')).hexdigest() + " recieved some inspiration", flush=True)

@bot.command()
@commands.check(permitted)
async def insult(ctx) :
    template = random.choice(insultList)
    insultString = requests.get("https://insult.mattbas.org/api/insult?template=" + urllib.parse.quote(template, safe ='')).text
    await ctx.channel.send('Oh, Elders of the AI, what slander do you grant for our foes?'+
        '\n\n *' + insultString.strip() + '*') 
    print(hashlib.md5(str(ctx.guild.id).encode('utf-8')).hexdigest() + " was hit with a devestating insult ", flush=True)

@bot.command()
async def help(ctx): # Ripped from QuoteBot
    response = discord.Embed()
    response.set_author(name = "More detailed docs here", url = "https://comhad.github.io/oujiabot/")

    response.description = (
                "Hello there! I am **OujiaBot**! I'm a bot made by [Comhad](https://twitter.com/AonanComhad)! " + 
                "My purpose of that is similar to **r/AskOujia** of reddit, when you issue `/ask`, " +
                "I will provide you with a sentence which contains a blank word, it is your job to put " + 
                "one letter at a time in seperate messages and fill in the blanks and fill in the blank word with friends!* Like this :\n\n" + 
                "```\nT\nH\nI\nS```\n\n" +
                "Once you are done, just say goodbye, and i will put it all into a string!\n\n" + 
                "I have some additional commands! They are : \n\n" + 
                "`/insult` - Use this command to get an AI generated insult!**\n\n" +
                "`/inspire` - Use this command to get 'inspiration' from inspirobot!**\n\n" +
                "`/mode` - Disable the above commands!\n\n"+
                "*The code prevents strings over " + str(characterLimit) + " characters so it doesn't have trouble sending them\n\n"
                "**These commands use APIs not moderated by me, and could output something potentially triggering, " + 
                " if you think this is not right for your server, please use `/mode` to disable them. (requies manage server permissions)")

    response.set_footer(text = "All the APIs used can be looked at in more detail at the link above", icon_url = bot.user.avatar_url)
    response.color = discord.Color.from_rgb(235, 52, 235) # A nice purple
    await ctx.send(embed = response)

# - - - Error handling here - - -

@bot.event
async def on_command_error(ctx, error) :
    if isinstance(error, discord.ext.commands.CommandNotFound) : # If a user runs a command we don't have
        return
        # It's really not important to do anything here

    elif isinstance(ctx.channel, discord.DMChannel) : # If the user asks a command in DM's
        await ctx.channel.send("Sorry, commands do not work in DM's!")
        return
    
    elif isinstance(error, discord.ext.commands.errors.MissingPermissions) :
        await ctx.channel.send("Sorry, it doesn't look like you have permissions for that command! Make sure to read the docs on how commands work!")
        return

    elif isinstance(error, discord.ext.commands.errors.CheckFailure) :
        await ctx.channel.send("The command checks failed for this command! It may have been disabled in this server! You can undo this by typing `/mode`! (As long you have manager server permissions!)")
        return

    else : 
        await ctx.channel.send("Oh! Something went wrong sorry :(")
        print("An unhandled error occured " + str(error)) # If it's an error we don't expect, do NOT send back the error
    
@bot.event
async def on_message(message):
    if message.author == bot.user: # Don't respond to ourselves
        return

    if message.author.bot : # If this is a bot sending the message
        return

    if len(message.content) == 1 and message.guild != None : # Don't allow DM's
        if database.gameInProgress(message) :
            # If a game is in progess append the answer
            answer = database.appendToAnswer(message)
            if len(answer) > characterLimit :
                fullStatement = database.completeAnswer(message)
                await message.channel.send("Sorry, you've gone over the limit for characters in a answer!\nThe final statement was \n\n*" + fullStatement + "*")
    
    if message.content.lower() == "goodbye" and message.guild != None :
        if database.gameInProgress(message) :
            fullStatement = database.completeAnswer(message)
            await message.channel.send("Ask complete! The final statement was\n\n *" + fullStatement + "*")
    await bot.process_commands(message)
             
bot.intents.messages = True
# Allow ourselves to get notified when we join a new server etc.

bot.run(token)
