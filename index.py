import datetime
import random
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json


class Index(webapp.RequestHandler):
    def get(self):
        self.response.out.write('h')


application = webapp.WSGIApplication(
                                     [('/', Index)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
