import datetime
import random
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json
from mako.template import Template
from counter import Counter

class Index(webapp.RequestHandler):
    def get(self):

        
        template = Template(filename="index.html",
                            input_encoding='utf8',
                            output_encoding='utf8')
        
        distance = Counter.get_by_key_name('distance')

        output = template.render(kilometers=distance.value/1000)
        self.response.out.write(output)

application = webapp.WSGIApplication(
                                     [('/', Index)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
