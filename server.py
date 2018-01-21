from tornado import web
import tornado.ioloop, tornado.websocket
import tweepy
from textblob import TextBlob
import dataset
import settings
#Python Libraries
import time, datetime, threading

"""Creation of our websocket to communicate information to our users"""
class EstablishWebsocket(tornado.websocket.WebSocketHandler):

    #To keep track of all current websockets.
    websockets = []

    def open(self):
        print("Websocket opened.")
        self.websockets.append(self)

    def on_message(self, message):
        return
        #TODO
        #Load up all cached data to bring users up to date upon connecting.
        #We dont need to accept messages from the client.

    def on_close(self):
        print("Websocket is closing...")
        self.websockets.remove(self)
        self.close() #Close the connection once the user disconnects.


"""This section connects our streamer
   to the websocket, to receive updates from."""
TRACKING_TERMS = ['trump'] #Edit this value to change what to stream.

auth = tweepy.OAuthHandler(settings.consumer_key, settings.consumer_secret)
auth.set_access_token(settings.access_token, settings.access_token_secret)

#setting up database connections.
db = dataset.connect('sqlite:///database/twitter.db')
tweetDB = db['tweets']
value_table = db['score']

class StreamListener(tweepy.StreamListener, EstablishWebsocket):

    def on_status(self, status):
        #Prevents unusable tweets, to provide accurate information.
        if (status.retweeted) or ('RT @' in status.text):
            return

        polarity = TextBlob(status.text).sentiment.polarity
        if polarity == 0.0:
            return

        created_at = status.created_at.strftime('%Y-%m-%d %H:%M:%S')
        print(polarity)
        tweetDB.insert(dict(
            created_at = created_at,
            polarity = polarity
        ))


        out_dict = {'Tweet': status.text, 'Polarity': polarity, 'Created_at': created_at }
        #Write out the updated information to the clientsself.
        for websocket in EstablishWebsocket.websockets:
            websocket.write_message(out_dict)

    def on_error(self, error):
        if error == 420:
            return False

    def run_stream():
        """Method sets up our stream listener, and, uses filter to
        begin streaming tweets over a hashtag."""
        streamListener = StreamListener()
        stream = tweepy.Stream(auth, listener=streamListener)
        stream.filter(track=TRACKING_TERMS)

    def remove_redundantData():
        """Accesses the database and removes all information older than 7 days.
           Updates the score for users and continues to stream inputs. """
        #Send user "True" to update new from database


"""This section deals with Tornado routing, and setups."""
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #Pass our tracking terms, to display what we are streaming over.
        #And pass the database to display.
        self.render("templates/index.html", TRACKING_TERMS=TRACKING_TERMS)

def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/websocket', EstablishWebsocket),
        (r'/static/(.*)', web.StaticFileHandler, {'path': 'static/' }),
        ], autoreload=True) #Turn off autoreload when in production.

if __name__ == "__main__":
    threading.Thread(target=StreamListener.run_stream).start()
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
