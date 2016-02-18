import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_GENRE = 'Non-fiction'


# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def reposit_key(genre=DEFAULT_GENRE):
    return ndb.Key('genre', genre)




class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    
    author = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):

    def get(self):
        genre = self.request.get('genre',DEFAULT_GENRE)
        greetings_query = Greeting.query(
            ancestor=reposit_key(genre)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)


        template_values = {
            'greetings': greetings,
            'genre': urllib.quote_plus(genre),
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class Reposit(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        genre = self.request.get('genre',
                                          DEFAULT_GENRE)
        greeting = Greeting(parent=reposit_key(genre))


        greeting.author = self.request.get('author')
        greeting.content = self.request.get('content')
        greeting.put()

        query_params = {'genre': genre}
        self.redirect('/?' + urllib.urlencode(query_params))

    def get(self):
        genre = self.request.get('genre',DEFAULT_GENRE)
        greetings_query = Greeting.query(
            ancestor=reposit_key(genre)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)


        template_values = {
            'greetings': greetings,
            'genre': urllib.quote_plus(genre),
        }

        template = JINJA_ENVIRONMENT.get_template('display.html')
        self.response.write(template.render(template_values))

class Enter(webapp2.RequestHandler):

    def get(self):
        genre = self.request.get('genre',DEFAULT_GENRE)
        greetings_query = Greeting.query(
            ancestor=reposit_key(genre)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)


        template_values = {
            'greetings': greetings,
            'genre': urllib.quote_plus(genre),
        }

        template = JINJA_ENVIRONMENT.get_template('enter.html')
        self.response.write(template.render(template_values))

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        genre = self.request.get('genre',DEFAULT_GENRE)
        greeting = Greeting(parent=reposit_key(genre))


        greeting.author = self.request.get('author')
        greeting.content = self.request.get('content')
        greeting.put()

        query_params = {'genre': genre}
        self.redirect('/?' + urllib.urlencode(query_params))

class Search(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        genre = self.request.get('genre',
                                          DEFAULT_GENRE)
        greeting = Greeting(parent=reposit_key(genre))


        greeting.author = self.request.get('author')
        greeting.content = self.request.get('content')
        greeting.put()

        query_params = {'genre': genre}
	prram2 = {'author': greeting.author}
        self.redirect('/search?' + urllib.urlencode(query_params)+'?'+urllib.urlencode(prram2))

    def get(self):
        genre = self.request.get('genre',DEFAULT_GENRE)
        greetings_query = Greeting.query(
            ancestor=reposit_key(genre)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)


        template_values = {
            'author': self.request.get('author'),
            'greetings': greetings,
            'genre': urllib.quote_plus(genre),
        }

        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/enter', Enter),
    ('/display',Reposit),
    ('/search',Search),
], debug=True)
