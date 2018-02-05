from tornado import web
import tornado.ioloop, tornado.websocket
import tweepy
from textblob import TextBlob
import sqlite3
import settings
#Python Libraries
import datetime, threading, json

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
            #Connect to the database
            dbTemp = sqlite3.connect("database/twitter.db")
            cursorTemp = dbTemp.cursor()

            #Prevents unusable tweets, to provide accurate information.
            if (status.retweeted) or ('RT @' in status.text):
                return

            polarity = TextBlob(status.text).sentiment.polarity
            if polarity == 0.0:
                return

            created_at = (status.created_at.strftime('%Y-%m-%d %H:%M:%S.')+(datetime.datetime.now().strftime('%f')))

            cursorTemp.execute("INSERT INTO tweets VALUES (?,?)", (datetime.datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f'), polarity))
            dbTemp.commit()
            cursorTemp.close()

            out_dict = {'Tweet': status.text, 'Polarity': polarity, 'Created_at': created_at }
            #Write out the updated information to the clients.
            for websocket in EstablishWebsocket.websockets:
                websocket.write_message(out_dict)
        #end loop, call self.run_stream()

    def on_error(self, error):
        if error == 420:
            return False

    def run_stream():
        """Method sets up our stream listener, and, uses filter to
        begin streaming tweets over a hashtag."""
        streamListener = StreamListener()
        stream = tweepy.Stream(auth, listener=streamListener)
        stream.filter(track=TRACKING_TERMS)

    def remove_Data():
        """Accesses the database and removes all information older than 7 days.
           Updates the score for users and continues to stream inputs. """
        db = sqlite3.connect("/database/twitter.db")
        cursor = db.cursor()
        #Remove data older than 7 days.. Run each day.
        cursor.execute('''DELETE FROM tweets WHERE created_at <= date('now', '-7')''')
        db.commit()
        cursor.close()

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
        cursor.execute("SELECT created_at, polarity FROM tweets ORDER BY created_at ASC")
        self.write(json.dumps(cursor.fetchall()))
        cursor.close()

def make_app():
    initdb = sqlite3.connect("database/twitter.db")
    cursor = initdb.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tweets (created_at datetime, polarity float)''')
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
