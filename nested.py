import os
import webapp2
import jinja2


from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


# Document Model

class Document(db.Model):

    name = db.StringProperty(required = True)
    username = db.StringProperty()
    document = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    
    @classmethod
    def by_name(cls, name):
        d = Document.all().filter('name =', name).get()
        return d

    @classmethod
    def by_id(cls, did):
        return Document.get_by_id(did)

# User Model

class User(db.Model):
    
    name = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

    @classmethod
    def register(cls, name, password, email=''):
        return User(name=name, password=password, email=email)

# Main Handler

class Handler(webapp2.RequestHandler):

    # Render stuff
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        # Set user
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)     

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    # Cookies stuff
    def set_secure_cookie(self, name, val):
        cookie_val = val
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    # Check for user
    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

# Page handler
# Process requests and build responses

class HomePage(Handler):

    def get(self):
        self.render('home.html')

class DocumentsPage(Handler):

    def render_documents(self):
        
        if self.user:
            username = self.user.name
            documents = db.GqlQuery("SELECT * FROM Document WHERE username = :1 ORDER BY created DESC", username)
            return documents

    def get(self):

        documents = self.render_documents()

        if documents:
            self.render('documents.html', documents=documents)

        else:
            self.redirect('/login')

class DocumentPage(Handler):

    def get(self, document_id):
        doc = Document.by_id(int(document_id))

        if doc and self.user:
            if doc.username == self.user.name:
                self.render('permalink.html', doc=doc)

            else:
                self.redirect('/')

        else:
            #self.error(404)
            self.redirect('/')


class NewPage(Handler):

    def get(self):
        self.render('new.html')

# Save document
class SavePage(Handler):

    def post(self):

        #Get document parameters
        name = self.request.get('name')
        document = self.request.get('document')

        #Get user name
        uid = self.read_secure_cookie('user_id')
        user = User.by_id(int(uid))
        username = user.name
  
        d = Document(name=name, username=username, document=document)
        d.put()

# Delete document
class DeletePage(Handler):
    
    def post(self):
        
        document_id = self.request.get('id')

        #Get the key from id
        key = db.Key.from_path('Document', int(document_id))
        
        #Delete the document from key
        db.delete(key)

# Save document changes
class EditPage(Handler):

    def post(self):

        # Get document parameters
        new_name = self.request.get('new_name')
        new_document = self.request.get('new_document')
        document_id = self.request.get('id')
        
        # Get user name
        uid = self.read_secure_cookie('user_id')
        user = User.by_id(int(uid))
        username = user.name

        old_document = Document.by_id(int(document_id))
        old_name = old_document.name

        #Check if document name was changed
        if new_name == old_name:

            # If name was not changed, delete the older one
            key = db.Key.from_path('Document', int(document_id))
            db.delete(key)

            # and create a document with the new document content
            d = Document(name=old_name, username=username, document=new_document)
            d.put()            

        else:
            
            # Create a document with the new name and document content
            d = Document(name=new_name, username=username, document=new_document)
            d.put()

# Save configuration
class ConfigurationPage(Handler):

    def post(self):

        # Get document parameters
        name = self.request.get('name')
        document = self.request.get('document')
        document_id = self.request.get('id')
        
        # Get user name
        uid = self.read_secure_cookie('user_id')
        user = User.by_id(int(uid))
        username = user.name

        # Delete document from key
        key = db.Key.from_path('Document', int(document_id))
        db.delete(key)

        # Create a document with the new configuration
        d = Document(name=name, username=username, document=document)
        d.put()      

# User stuff
# Register User
class RegisterPage(Handler):

    def get(self):
        self.render('register.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        confirm_password = self.request.get('confirm_password')
        email = self.request.get('email')

        params = dict(username=username)
        have_error = False

        if not username:
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not password:
            params['error_password'] = "That wasn't a valid password."
            have_error = True

        if not password == confirm_password:
            params['error_password'] = 'Passwords must match.'
            have_error = True
        
        if have_error:
            self.render('register.html', **params)
        
        else:
            #Check if a user with that name already exists. If not, create it.
            u = User.by_name(username)
            if u:
                params['error_username'] = 'That user already exists.'
                self.render('register.html', **params)
            
            else:
                u = User.register(username, password, email)
                u.put()

                self.login(u)
                self.redirect('/documents')

def valid_password(user, password):
    if user.password == password:
        return user

# Login
class LoginPage(Handler):

    def get(self):
        self.render('login.html')

    def post(self):
        logged = False
        username = self.request.get('username')
        password = self.request.get('password')

        user = User.by_name(username)

        if user:
            if valid_password(user, password):
                self.login(user)
                logged = True
                self.redirect('/documents')
                             
        if not logged:
            msg = 'Invalid login'
            self.render('login.html', error = msg)

class LogoutPage(Handler):

    def get(self):
        self.logout()
        self.redirect('/')

class AboutPage(Handler):

    def get(self):
        self.render('about.html')

class GuestPage(Handler):

    def get(self):
        user = User.by_name('Guest')
        self.login(user)
        self.redirect('documents')


# Run the application
# Routes incoming requests to handlers based on the URL
# Testing git branching
        
app = webapp2.WSGIApplication( [('/', HomePage), 
                                ('/documents', DocumentsPage), 
                                ('/documents/([0-9]+)', DocumentPage),
                                ('/new', NewPage),
                                ('/register', RegisterPage),
                                ('/login', LoginPage),
                                ('/logout', LogoutPage),
                                ('/save', SavePage),
                                ('/delete', DeletePage),
                                ('/edit', EditPage),
                                ('/configuration', ConfigurationPage),
                                ('/about', AboutPage),
                                ('/guest', GuestPage)], 
                                debug=True)

