from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class Marketplace(webapp.RequestHandler):
    def get(self):
        self.response.set_status(301)
        self.response.headers['Location'] = 'market://search?q=pname:hu.budapestcycletrack' 
        self.response.out.write('market://search?q=pname:hu.budapestcycletrack')

class Appstore(webapp.RequestHandler):
    def get(self):
        self.response.set_status(301)
        self.response.headers['Location'] = 'http://itunes.apple.com/hu/app/budapest-cycle-tracker/id433400907?mt=8' 
        self.response.out.write('http://itunes.apple.com/hu/app/budapest-cycle-tracker/id433400907?mt=8')

application = webapp.WSGIApplication(
                                     [('/marketplace', Marketplace),
                                      ('/appstore', Appstore)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
