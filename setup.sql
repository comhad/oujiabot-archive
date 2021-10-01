CREATE TABLE games (
    id INTEGER PRIMARY KEY ASC,
    question TEXT,
    answer TEXT,
    serverid TEXT,
    channel TEXT,
    active INTEGER,
    startedat TEXT
);

CREATE TABLE blockedAPI (
    guildId TEXT
);