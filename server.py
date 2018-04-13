from tornado import web
import sqlite3
import hashlib, uuid
import tornado.ioloop
from streamer.streamListener import StreamListener
from handlers.dataHandler import DataHandler
from handlers.websocketHandler import EstablishWebsocket
import tweepy
import settings
#Python Libraries
import threading, signal, time

streams = []
tracking = []

def signal_handler(signum, frame):
    """Trigger when CTRL + C called, Exit program and socket loop."""
    tornado.ioloop.IOLoop.current().stop()
    print("Stopped socket, Exit manually.")


class BaseHandler(tornado.web.RequestHandler):
    """Check if user is currently logged in."""
    def get_current_user(self):
        return self.get_secure_cookie("user")


class LoginHandler(BaseHandler):
    def get(self):
        if self.current_user:
            self.redirect("/admin")
            return
        else:
            self.write('<html><body><form action="/login" method="post">'
                       'Name: <input type="text" name="name" required/><br>'
                       'Password: <input type="password" name="pswd" required/><br>'
                       '<input type="submit" value="Sign in">'
                       '</form></body></html>')

    def post(self):
        initdb = sqlite3.connect("database/twitter.db")
        initdb.row_factory = sqlite3.Row
        cursor = initdb.cursor()
        #Get current salt and hashed password.
        cursor.execute('''SELECT username, password, salt FROM admin
                            WHERE username=?''',(self.get_argument("name"),))
        dbVal = cursor.fetchone()
        if dbVal == None:
            self.redirect("/login")
        else:
            if hashlib.sha512(str(self.get_argument("pswd") + dbVal['salt']).encode('utf-8')).hexdigest() == dbVal['password']:
                self.set_secure_cookie("user", self.get_argument("name"))
                self.redirect("/admin")
            else: self.redirect("/login")
        cursor.close()
        initdb.close()


class LogoutHandler(BaseHandler):
    def get(self):
        if self.current_user:
            self.clear_cookie("user")
        self.redirect("/")


class AdminHandler(BaseHandler):
    """Allows the admin to change the stream."""
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        else:
            self.render("templates/admin.html", TRACKING_TERMS=tracking)


class MainHandler(BaseHandler):
    def get(self):
        """This section deals with Tornado routing, home page loaded within index.html"""
        self.render("templates/index.html", TRACKING_TERMS=tracking)

    def post(self):
        global tracking
        global streams
        if not self.current_user:
            return
        else:
            #Load previous stream.
            for stream in streams:
                stream.disconnect()

            tracking = [self.get_argument("topic")]
            streamListener = StreamListener()
            streamListener.clearDB()
            tOne = threading.Thread(target=streamListener.run_stream, args=([self.get_argument("topic")],))
            tOne.setDaemon(True)
            tOne.start()

            #Wait for updates to be made.
            time.sleep(1)
            streams.append(streamListener.current_stream)
            self.render("templates/index.html", TRACKING_TERMS=tracking)

def make_app():

    settings.create_tables()

    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/getdata', DataHandler),
        (r'/websocket', EstablishWebsocket),
        (r'/login', LoginHandler),
        (r'/logout', LogoutHandler),
        (r'/admin', AdminHandler),
        (r'/static/(.*)', web.StaticFileHandler, {'path': 'static/' }),
        ], cookie_secret="z[+cEmNe3$14ftWqms}QYy[S6ULGMBE~E5r9l3UYm.*X4wAMuG") #Turn off autoreload when in production.

if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    signal.signal(signal.SIGINT, signal_handler)
    tornado.ioloop.IOLoop.current().start()
