import datetime
import sqlite3
import hashlib, uuid

consumer_key = ''
consumer_secret = ''
access_token = '-'
access_token_secret = ''

password="KCLStreamer"
salt = uuid.uuid4().hex
hashed_password = hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest()



def create_tables():
    #Create both databases (Testing and non-Testing) if not existing.
    database = ["database/twitter.db","database/test-twitter.db"]
    for x in database:
        initdb = sqlite3.connect(x)
        cursor = initdb.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tweet (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at DATETIME, polarity FLOAT, tweet_text TEXT, subjectivity FLOAT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS word (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        word_val TEXT, word_count INT, polarity BOOLEAN)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS tweet_word (tweet_id INTEGER, word_id INTEGER,
                        FOREIGN KEY(tweet_id) REFERENCES tweet(id),
                        FOREIGN KEY(word_id) REFERENCES word(id))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS admin (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT, password TEXT, salt TEXT)''')

        cursor.execute("SELECT username FROM admin WHERE username = ?",("admin",))
        if cursor.fetchone() == None: cursor.execute('''INSERT INTO admin VALUES(NULL,?,?,?)''',("admin",hashed_password, salt))

        initdb.commit()
        cursor.close()
        initdb.close()
