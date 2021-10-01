# OujiaBot archived code
The source code to the OujiaBot bot I no longer host

This was my first discord bot, I created it in 2020 for me and my friends discord server.
I eventually published the bot in febuary 2021 and it got a lot of use, and I could see from analytics some servers where having a lot of fun with it!
However, eventually there became less and less use till there was no use of the bot for months at a time, and it was losing servers.
OujiaBot was deactivated in september 2021 and taken offline forever due to lack of use.

Don't attack me for my awful programming here, I was a complete newbie when writing this, but it works.

# How to run it
To run OujiaBot, you need to go through a few steps first :

*Linux instructions*

1. Install [discord.py](https://github.com/Rapptz/discord.py/), you can use `python3 -m pip install discord.py`.
2. Make the sqlite3 database, use `sqlite3 server_info.db` and then type `.read setup.sql` to read the SQL and create the tables.
3. Make a JSON file called `auth.json` and copy the following into it :
```
{
    "bot" : "<token>"
}
```
4. Replace `<token>` with your bot token, if you don't have a bot token and want to know how to make one, see [this](https://discordpy.readthedocs.io/en/stable/discord.html)
5. Run the bot using `python3 main.py`, if it doesn't crash instantly, you can invite and use it.

# Customizations
You can change the things the bot says by changing the files :
+ `main.py` can be changed to alter the command prefix, change the slash (`/`) in `command_prefix='/'` to whatever you want the prefix to be.
+ `questions.txt` can be changed to include different questions for the `ask` command, include four underscores (`____`) where you want the answer to be placed.
+ `insults.txt` can be changed to include different outputs for the `insult` command

# Changes
This bot isn't really active anymore, I don't think it's worth adding anymore features, pull requests and issues for only be made for security vulnerabilities.