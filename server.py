from tornado import web
import tornado.ioloop
import tornado.websocket
import tweepy
import threading
import settings
from textblob import TextBlob
import dataset

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


"""This section deals with Tornados  routing, and setups."""
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #Pass our tracking terms, to display what we are streaming over.
        self.render("templates/index.html", TRACKING_TERMS=TRACKING_TERMS)

def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/websocket', EstablishWebsocket),
        (r'/static/(.*)', web.StaticFileHandler, {'path': 'static/' }),
        ], autoreload=True) #Turn off autoreload when in production.




"""This section connects our streamer
   to the websocket, to receive updates from."""
TRACKING_TERMS = ['#uk'] #Edit this value to change what to stream.

auth = tweepy.OAuthHandler(settings.consumer_key, settings.consumer_secret)
auth.set_access_token(settings.access_token, settings.access_token_secret)

#setting up database connections.
db = dataset.connect('sqlite:///database/twitter.db')
table = db['tweets']
value_table = db['score']

class StreamListener(tweepy.StreamListener, EstablishWebsocket):

    def on_status(self, status):
        #Prevents unusable tweets, to provide accurate information.
        if (status.retweeted) or ('RT @' in status.text):
            return

        polarity = TextBlob(status.text).sentiment.polarity
        if polarity == 0.0:
            return

        table.insert(dict(
            created_at = status.created_at,
            polarity = polarity
        ))
        print(polarity)
        string = str(polarity)
        out_dict = {'Tweet': status.text, 'Polarity': string }
        #Write out the updated information to the clients.
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



if __name__ == "__main__":
    threading.Thread(target=StreamListener.run_stream).start()
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
