import datetime
import random
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json
from counter import Counter

class Track(db.Model):
    uuid = db.StringProperty()
    uploadtime = db.DateTimeProperty()
    distance = db.IntegerProperty()
    raw = db.TextProperty()

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
            
            distance = int(data['distance'])
            track = Track(uuid=data['uuid'], uploadtime=uploadtime, distance=distance)
            
            counter = Counter.get_by_key_name('distance')
            if not counter:
                counter = Counter(key_name='distance',value=24000)
            counter.value += distance
            counter.put()

            number = Counter.get_by_key_name('number')
            if not number:
                number = Counter(key_name='number',value=130)
            number.value += 1
            number.put()

            track.raw = trk
            track.put()

#            for p in data['track']:
#                point = Point(parent=track, lat=p['lat'], lng=p['long'], acc=p['acc'], ts=datetime.datetime.fromtimestamp(p['ts']))
#                point.put()

            self.response.out.write('{"success":true}')
        except Err, e:
            self.response.out.write('{"success":false, "error":"%s"}' % e.message)
            

class Stats(webapp.RequestHandler):
    def get(self):
        dist = Counter.get_by_key_name('distance')
        totaldistance = dist.value

        number = Counter.get_by_key_name('number')
        totaltracks = number.value

        self.response.out.write('{"totalDistance":%d, "totalTracks":%d}' % (totaldistance, totaltracks))

application = webapp.WSGIApplication(
                                     [('/upload', Upload),
                                      ('/stats', Stats)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
