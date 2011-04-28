import datetime
import random
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json

class Track(db.Model):
    uuid = db.StringProperty()
    uploadtime = db.DateTimeProperty()
    distance = db.IntegerProperty()

class Point(db.Model):
    lat = db.FloatProperty()
    lng = db.FloatProperty()
    ts = db.DateTimeProperty()
    acc = db.IntegerProperty()

class Err(Exception):
    pass

class Upload(webapp.RequestHandler):
    def post(self):
        try:
            decoder = json.JSONDecoder()
            trk = self.request.get('track')
            if not trk:
                raise Err("no track found")
                            
            data = decoder.decode(trk)
            uploadtime = datetime.datetime.now()
            
            track = Track(uuid=data['uuid'], uploadtime=uploadtime, distance=int(data['distance']))
            track.put()

            for p in data['track']:
                point = Point(parent=track, lat=p['lat'], lng=p['long'], acc=p['acc'], ts=datetime.datetime.fromtimestamp(p['ts']))
                point.put()

            self.response.out.write('{"success":true}')
        except Err, e:
            self.response.out.write('{"success":false, "error":"%s"}' % e.message)
            

class Stats(webapp.RequestHandler):
    def get(self):
        totaldistance = 23000
        totaltracks = 127
        self.response.out.write('{"totalDistance":%d, "totalTracks":%d}' % (totaldistance, totaltracks))

application = webapp.WSGIApplication(
                                     [('/upload', Upload),
                                      ('/stats', Stats)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
