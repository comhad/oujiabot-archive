import sqlite3, hashlib, datetime

class serverInfo :
    connection = sqlite3.connect("server_info.db")
    cursor = connection.cursor()

    def checkServer(self, message) :
        guildId = hashlib.md5(str(message.guild.id).encode('utf-8')).hexdigest()
        row = self.cursor.execute("SELECT * FROM blockedAPI where guildId = (?)", (guildId,)).fetchone()
        if row == None :
            return True # If there is no row marking this as disabled
        return False

    def addServer(self, message) : # Add server to restricted list
        guildId = hashlib.md5(str(message.guild.id).encode('utf-8')).hexdigest()
        self.cursor.execute("INSERT INTO blockedAPI values (?)", (guildId,))
        self.connection.commit()
        return

    def removeServer(self, message) : # Remove server from restricted list
        guildId = hashlib.md5(str(message.guild.id).encode('utf-8')).hexdigest()
        self.cursor.execute("DELETE FROM blockedAPI where guildId = (?)", (guildId,))
        self.connection.commit()
        return
    
    def startGame(self, question, message) :
        # Don't run this function for games in DM's, it WILL break
        serverId = hashlib.md5(str(message.guild.id).encode('utf-8')).hexdigest()
        channelId = hashlib.md5(str(message.channel.id).encode('utf-8')).hexdigest()
        # We can't hash the channel id, because the code may need to cleanup and send messages saying statements are being shut off
        self.cursor.execute("INSERT INTO games (serverid, question, channel, answer, active, startedat) VALUES (?, ?, ?, ?, ?, ?)", 
        (serverId, question, channelId, "", 1, str(datetime.datetime.now()),))
        self.connection.commit()

    def gameInProgress(self, message) :
        # Don't run this function for games in DM's, it WILL break
        serverId = hashlib.md5(str(message.guild.id).encode('utf-8')).hexdigest()
        channelId = hashlib.md5(str(message.channel.id).encode('utf-8')).hexdigest()
        row = self.cursor.execute("SELECT question from games where active = (1) and serverid = (?) and channel = (?)", (serverId, channelId,)).fetchone()
        if row == None :
            return False
        return row[0] 
        # Return the question if active
    
    def appendToAnswer(self, message) :
        # This function relies on if there is a running game on already, check before calling
        serverId = hashlib.md5(str(message.guild.id).encode('utf-8')).hexdigest()
        channelId = hashlib.md5(str(message.channel.id).encode('utf-8')).hexdigest()
        row = self.cursor.execute("SELECT answer from games where active = (1) and serverid = (?) and channel = (?)", (serverId, channelId,)).fetchone()
        answer = row[0] + message.content.upper()
        self.cursor.execute("UPDATE games set answer = (?) where serverid = (?) and channel = (?) and active = (1)", (answer, serverId, channelId,))
        self.connection.commit()
        return answer
    
    def completeAnswer(self, message) :
        # This function relies on if there is a running game on already, check before calling
        serverId = hashlib.md5(str(message.guild.id).encode('utf-8')).hexdigest()
        channelId = hashlib.md5(str(message.channel.id).encode('utf-8')).hexdigest()
        row = self.cursor.execute("SELECT question, answer from games where active = (1) and serverid = (?) and channel = (?)", (serverId, channelId,)).fetchone()
        question = row[0]
        answer = row[1]
        self.cursor.execute("UPDATE games set active = (0) where serverid = (?) and channel = (?)", (serverId, channelId,))
        self.connection.commit()
        return question.replace("____", answer)