from tornado import web
import tornado.ioloop, tornado.websocket
import tweepy
import signal
from textblob import TextBlob
import sqlite3
import settings
#Python Libraries
import datetime, threading, json, time

TRACKING_TERMS = ['school'] #Edit this value to change what to stream.

def signal_handler(signum, frame):
    """Trigger when CTRL + C called, Exit program and socket loop."""
    tornado.ioloop.IOLoop.current().stop()
    print("Stopped socket, Exit manually.")


class EstablishWebsocket(tornado.websocket.WebSocketHandler):
    """Creation of the websocket to communicate information
     to users"""
    #To keep track of all current websockets.
    websockets = []

    def open(self):
        print("Websocket opened.")
        self.websockets.append(self)

    def on_message(self, message):
        return

    def on_close(self):
        print("Websocket is closing...")
        self.websockets.remove(self)
        self.close() #Close the connection once the user disconnects.


"""This section connects our streamer
   to the websocket, to receive updates from."""
auth = tweepy.OAuthHandler(settings.consumer_key, settings.consumer_secret)
auth.set_access_token(settings.access_token, settings.access_token_secret)

class StreamListener(tweepy.StreamListener):

    def on_status(self, status):
        #while time != 00:00..do
        #Prevents unusable tweets, to provide accurate information.
        statusText = status.text
        if (status.retweeted) or ('RT @' in statusText) or ('t.co' in statusText):
            return

        text = TextBlob(statusText)
        polarity = text.sentiment.polarity
        if polarity == 0.0:
            return
        #Add a millisecond timestamp for accuracy and eliminate collisions.
        created_at = (status.created_at.strftime('%Y-%m-%dT%H:%M:%S.')+(datetime.datetime.now().strftime('%f')))
        polarityBool = polarity > 0.0
        #Connect to the database and push to the database
        dbTemp = sqlite3.connect("database/twitter.db")
        cursorTemp = dbTemp.cursor()
        textTags = text.tags
        cursorTemp.execute("INSERT INTO tweet VALUES (NULL,?,?,?)", (created_at,
                            polarity, statusText))
        tweet_id = cursorTemp.lastrowid
        for word, tag in textTags:
            if(tag == "NN" or tag == "NNS" or tag == "NPS" or tag == "NP") and (len(word) != 1):
                cursorTemp.execute("SELECT * FROM word WHERE word_val=? AND polarity=?", (word, polarityBool))
                entry = cursorTemp.fetchone()

                if entry is None:
                    cursorTemp.execute("INSERT INTO word VALUES (NULL,?,?,?)",
                                        (word, 1, polarityBool))
                    word_id = cursorTemp.lastrowid
                else:
                    cursorTemp.execute("UPDATE word SET word_count=word_count+1 WHERE word_val=? AND polarity=?",
                                        (word, polarityBool))
                    #Get the ID value to insert into tweet_word.
                    word_id = entry[0]

                #Add relationship to tweet. For ability to extract a words' tweets
                cursorTemp.execute("INSERT INTO tweet_word VALUES (?,?)",
                                    (tweet_id, word_id))
        dbTemp.commit()
        cursorTemp.close()

        #Dictionary to be parsed to clients browsers.
        out_dict = {'Tweet': status.text, 'Polarity': polarity, 'Created_at': created_at, 'Pie_val' : round(polarity, 0)}
        #Write out the updated information as a dict object to the clients.
        for websocket in EstablishWebsocket.websockets:
            try:
                websocket.write_message(out_dict)
            except:
                #Ignore, Once clients disconnect, simply prevent sending information
                pass


    def on_error(self, error):
        print(error)

    def remove_Data():
        """Accesses the database and removes all information older than 7 days.
            Updates the score for users and continues to stream inputs."""
        db = sqlite3.connect("/database/twitter.db")
        cursor = db.cursor()
        #Remove data older than 7 days.. Run each day.
        cursor.execute('''DELETE FROM tweets WHERE date('now', '-7')''')
        db.commit()
        cursor.close()
        db.close()

    def run_stream():
        """Method sets up our stream listener, and, uses filter to
        begin streaming tweets over a hashtag."""
        streamListener = StreamListener()
        stream = tweepy.Stream(auth, listener=streamListener)
        stream.filter(track=TRACKING_TERMS)


"""This section deals with Tornado routing, and setups."""
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #Pass our tracking terms, to display what we are streaming over.
        #And pass the database to display.
        self.render("templates/index.html", TRACKING_TERMS=TRACKING_TERMS)

class DataHandler(tornado.web.RequestHandler):
    def get(self):
        """Method to return information to populate the
            webpage"""

        key = self.get_argument('key', None)
        response = {'key' : key}
        get_data = {}
        db = sqlite3.connect("database/twitter.db")
        cursor = db.cursor()

        if key == 'dayBtn':
            cursor.execute("SELECT created_at, polarity FROM tweet ORDER BY created_at ASC")
            get_data.update({'0': cursor.fetchall()})

        elif key == 'hourBtn':
            cursor.execute("SELECT created_at, polarity FROM tweet WHERE date('now', '-1 day') ORDER BY created_at ASC")
            get_data.update({'0': cursor.fetchall()})

        elif key == None:

            sql = ('''SELECT created_at, polarity FROM tweet ORDER BY created_at ASC;
            SELECT COUNT(*) FROM tweet WHERE polarity >= 0.7;
            SELECT COUNT(*) FROM tweet WHERE polarity <= -0.7;
            SELECT word_val FROM word WHERE  polarity = 1 ORDER BY word_count DESC limit 10;
            SELECT word_val FROM word WHERE  polarity = 0 ORDER BY word_count DESC limit 10''')

            for count, result in enumerate(sql.split(';')):
                values = cursor.execute(result)
                get_data.update({count : cursor.fetchall()})

        self.write(json.dumps(get_data))
        cursor.close()
        db.close()

def make_app():
    initdb = sqlite3.connect("database/twitter.db")
    cursor = initdb.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tweet (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at DATETIME, polarity FLOAT, tweet_text TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS word (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word_val TEXT, word_count INT, polarity BOOLEAN)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS tweet_word (tweet_id INTEGER, word_id INTEGER,
                    FOREIGN KEY(tweet_id) REFERENCES tweet(id),
                    FOREIGN KEY(word_id) REFERENCES word(id))''')
    cursor.close()
    initdb.close()

    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/getdata', DataHandler),
        (r'/websocket', EstablishWebsocket),
        (r'/static/(.*)', web.StaticFileHandler, {'path': 'static/' }),
        ], autoreload=True) #Turn off autoreload when in production.

if __name__ == "__main__":
    t = threading.Thread(target=StreamListener.run_stream)
    #Close when main thread has ended.
    t.setDaemon(True)
    t.start()
    app = make_app()
    app.listen(8080)
    signal.signal(signal.SIGINT, signal_handler)
    tornado.ioloop.IOLoop.current().start()
