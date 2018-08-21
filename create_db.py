#!/usr/bin/python3

import sqlite3

conn = sqlite3.connect('assn2.db')
print ("Opened database successfully");

conn.execute('''DROP TABLE IF EXISTS users;''')
conn.execute('''CREATE TABLE Users
       (ZID  TEXT PRIMARY KEY     NOT NULL,
        password       TEXT,
        full_name           TEXT    NOT NULL,
       birthday       TEXT,
       email          TEXT,
       program        TEXT,
       home_suburb    TEXT,
        longitude      TEXT  ,
       latitude       TEXT,
       intro          TEXT);''')
#toID is a foeign key from users table
conn.execute('''DROP TABLE IF EXISTS posts;''')
conn.execute('''CREATE TABLE Posts
       (ID int PRIMARY KEY     NOT NULL,
       zID               TEXT,
       fromID           TEXT,
       posttime           TEXT  ,
       latitutude        TEXT    ,
       longitude        INT     ,
       message           TEXT,
       commentID         int,
       replyID          int);''')

#zid = users.id    friend = users.id
conn.execute('''DROP TABLE IF EXISTS friends;''')
conn.execute('''CREATE TABLE friends
       (ZID text     NOT NULL,
        friend text   NOT NULL,
        status int  NOT NULL,
        FOREIGN KEY(ZID) REFERENCES users(ZID),
        FOREIGN KEY(friend) REFERENCES users(Zid));''')

#zid = user.id course = text
conn.execute('''DROP TABLE IF EXISTS courses;''')
conn.execute('''CREATE TABLE courses
        (ZID TEXT    NOT NULL,
        course text    NOT NULL,
        FOREIGN KEY(ZID) REFERENCES users(ZID));''')


print ("Table created successfully");

conn.close()
