import datetime
import random
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json
from mako.template import Template


class Index(webapp.RequestHandler):
    def get(self):

        
        template = Template(filename="index.html",
                            input_encoding='utf8',
                            output_encoding='utf8')

        output = template.render(kilometers=9999)
        self.response.out.write(output)

application = webapp.WSGIApplication(
                                     [('/', Index)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
