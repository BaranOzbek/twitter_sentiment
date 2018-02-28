from tornado import web
import tornado.ioloop, tornado.websocket
import tweepy
from textblob import TextBlob
import sqlite3
import settings
#Python Libraries
import datetime, threading, json, time

TRACKING_TERMS = ['uk'] #Edit this value to change what to stream.

"""Creation of our websocket to communicate information to our users"""
class EstablishWebsocket(tornado.websocket.WebSocketHandler):

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

class StreamListener(tweepy.StreamListener, EstablishWebsocket):

    def on_status(self, status):
        #while time != 00:00..do
        #Prevents unusable tweets, to provide accurate information.
        if (status.retweeted) or ('RT @' in status.text):
            return

        text = TextBlob(status.text)
        polarity = text.sentiment.polarity

        if polarity == 0.0:
            return

        created_at = (status.created_at.strftime('%Y-%m-%dT%H:%M:%S.')+(datetime.datetime.now().strftime('%f')))

        #Connect to the database and push to the database
        dbTemp = sqlite3.connect("database/twitter.db")
        cursorTemp = dbTemp.cursor()
        cursorTemp.execute("INSERT INTO tweets VALUES (?,?)", (created_at,
                            polarity))
        dbTemp.commit()
        cursorTemp.close()

        if (polarity >= 0.7) or (polarity <= -0.7):
            #Add to get the percentages
            out_dict = {'Tweet': status.text, 'Polarity': polarity, 'Created_at': created_at, 'Pie_val' : round(polarity, 1)}
        else:
            out_dict = {'Tweet': status.text, 'Polarity': polarity, 'Created_at': created_at, 'Pie_val' : 0}

        #Write out the updated information as a dict object to the clients.
        for websocket in EstablishWebsocket.websockets:
            websocket.write_message(out_dict)

    def on_error(self, error):
        print(error)

    def remove_Data():
        """Accesses the database and removes all information older than 7 days.
            Updates the score for us    ers and continues to stream inputs."""
        db = sqlite3.connect("/database/twitter.db")
        cursor = db.cursor()
        #Remove data older than 7 days.. Run each day.
        cursor.execute('''DELETE FROM tweets WHERE created_at <= date('now', '-7')''')
        db.commit()
        cursor.close()

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

        db = sqlite3.connect("database/twitter.db")
        cursor = db.cursor()
        sql = ('''SELECT created_at, polarity FROM tweets ORDER BY created_at ASC;
        SELECT COUNT(*) FROM tweets WHERE polarity >= 0.7;
        SELECT COUNT(*) FROM tweets WHERE polarity <= -0.7''')

        get_data = {}
        for count, result in enumerate(sql.split(';')):
            values = cursor.execute(result)
            get_data.update({count : cursor.fetchall()})

        self.write(json.dumps(get_data))
        cursor.close()

def make_app():
    initdb = sqlite3.connect("database/twitter.db")
    cursor = initdb.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tweets (created_at TEXT, polarity FLOAT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS words (word TEXT, word_count INT, polarity BOOLEAN)''')
    cursor.close()

    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/getdata.json', DataHandler),
        (r'/websocket', EstablishWebsocket),
        (r'/static/(.*)', web.StaticFileHandler, {'path': 'static/' }),
        ], autoreload=True) #Turn off autoreload when in production.

if __name__ == "__main__":
    threading.Thread(target=StreamListener.run_stream).start()
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
