import os
import urllib
import random

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_GENRE = 'Non-fiction'
DEFAULT_AUTHOR = 'shabishabi'
DEFAULT_ERROR  = 'false'

# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def reposit_key(genre=DEFAULT_GENRE):
    return ndb.Key('genre', genre.lower())

def cart_key(user):
    return ndb.Key('User', user)


class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    id = ndb.StringProperty(indexed=True)   
    author = ndb.StringProperty(indexed=False)
    price = ndb.FloatProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class Cart(ndb.Model):
    book_id = ndb.StringProperty()  
    book_genre = ndb.StringProperty()

class MainPage(webapp2.RequestHandler):

    def get(self):
	cookie_id = self.request.cookies.get('key')  
        if cookie_id == None:
            cookie_id = str(random.randint(1000000000, 9999999999))
	
	user = users.get_current_user()  
        if user:
            url = users.create_logout_url('/')
            nickname = user.nickname()
            hasLogin = True
        else:
            url = users.create_login_url('/')
            nickname = ''
            hasLogin = False    

        genre = self.request.get('genre',DEFAULT_GENRE)
        greetings_query = Greeting.query(
            ancestor=reposit_key(genre)).order(-Greeting.date)
        greetings = greetings_query.fetch(100)


        template_values = {
            'greetings': greetings,
            'genre': urllib.quote_plus(genre),
	    'url': url,
            'nickname': nickname,
            'hasLogin': hasLogin,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
	self.response.headers.add_header('Set-Cookie', 'key=%s' % str(cookie_id))

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
        greetings = greetings_query.fetch(100)


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
        greetings = greetings_query.fetch(100)

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
        genre = self.request.get('genre')
        greeting = Greeting(parent=reposit_key(genre))
	query_params = {'genre': genre}
        def generateId():  
            CHAR = [chr(i) for i in xrange(ord('A'), ord('Z')+1)] \
                    + [chr(i) for i in xrange(ord('a'), ord('z')+1)] \
                    + [chr(i) for i in xrange(ord('0'), ord('9')+1)]
            book_id = ''
            for i in xrange(20):
                book_id += CHAR[random.randint(0, len(CHAR) - 1)]
            return book_id
        greeting.id = generateId()
        is_float = True  
        try:
            greeting.price = float(self.request.get('price'))        
        except:
            is_float = False

        greeting.author = self.request.get('author')
        greeting.content = self.request.get('content')
	if greeting.author != '' and greeting.content != '' and is_float:
            greeting.put()
            self.redirect('/?' + urllib.urlencode(query_params))
        else:
            query_param2 = {'error': 'true'}
            self.redirect('/enter?' + urllib.urlencode(query_param1) + '&' + urllib.urlencode(query_param2))


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
        greetings = greetings_query.fetch(100)


        template_values = {
            'author': self.request.get('author'),
            'greetings': greetings,
            'genre': urllib.quote_plus(genre),
        }

        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))
class EnterCart(webapp2.RequestHandler):
    
    def post(self):
        user = users.get_current_user()
        if not user:
            user = self.request.cookies.get('key')
        else:
            user = user.email()
        greetings = self.request.get('book', allow_multiple=True)  
        for greeting in greetings:
            cart = Cart(parent=cart_key(user))
            tokens = greeting.split('##')
            book_id, book_genre = tokens[0], tokens[1]
            cart.book_id = book_id  
            cart.book_genre = book_genre
            cart.put()
        self.redirect('/cart?' + urllib.urlencode({'user': user}))

class ShowCart(webapp2.RequestHandler):
    
    def get(self):
        user = users.get_current_user()
        user_name = 'false'
        if not user:
            user = self.request.cookies.get('key')
        else:
            user = user.email()
            user_name = user
            cookie_id = self.request.cookies.get('key')
            cart_temp = Cart.query(ancestor=cart_key(cookie_id))
            if cart_temp:  
                for book in cart_temp:
                    cart = Cart(parent=cart_key(user))
                    cart.book_id = book.book_id
                    cart.book_genre = book.book_genre
                    cart.put()
                    book.key.delete() 
        cart = Cart.query(ancestor=cart_key(user))    
        
        total = 0
        books = []
        for item in cart:  
            book = Greeting.query(ancestor=reposit_key(item.book_genre.lower())).filter(Greeting.id == item.book_id).fetch(1)            
            total += book[0].price
            books.extend(book)
        
        template_values = {
            'cart': books,
            'total': total,
            'checkout': self.request.get('checkout'),
            'user_name': user_name,
        }

        template = JINJA_ENVIRONMENT.get_template('cart.html')
        self.response.write(template.render(template_values))                

class CartMoves(webapp2.RequestHandler):
    
    def post(self):
        
        button_checkout = self.request.get("checkout")  
        button_remove = self.request.get("remove")
        
        if button_checkout:  
            user = users.get_current_user()
            if user == None:
                url = users.create_login_url('/cart')
                self.redirect(url)              
            else:
                user = user.email()       
                cart_temp = Cart.query(ancestor=cart_key(user))
                for greeting in cart_temp:
                    greeting.key.delete()
                self.redirect('/cart?' + urllib.urlencode({'user': user}) + '&' + urllib.urlencode({'checkout': 'true'}))
        
        if button_remove:  
            book_id = button_remove  
            user = users.get_current_user()
            if not user:
                user = self.request.cookies.get('key')
            else:
                user = user.email()
            cart = Cart.query(ancestor=cart_key(user))
            for greeting in cart:
                if greeting.book_id == book_id:  
                    greeting.key.delete()
                    break
            self.redirect('/cart?' + urllib.urlencode({'user': user}))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/enter', Enter),
    ('/display',Reposit),
    ('/search',Search),
    ('/add-to-cart', EnterCart),
    ('/cart', ShowCart),
    ('/cart-moves', CartMoves),
], debug=True)
