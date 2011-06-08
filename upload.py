import datetime
import logging
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

    @staticmethod
    def get_all(offset):
        return db.GqlQuery('SELECT * FROM Track LIMIT 100 OFFSET %s' % offset)

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

class AndroidIphone(webapp.RequestHandler):
    def get(self):
        tracks = Track.get_all()
        iphone = 0
        android = 0
        other = 0
        iphone_dist = 0
        android_dist = 0
        other_dist = 0
        iphone_devs = {}
        android_devs = {}
        other_devs = {}
        for t in tracks:
            if '-' in t.uuid:
                other += 1
                other_dist += t.distance
                other_devs[t.uuid] = True
            elif len(t.uuid) == 40:
                iphone += 1
                iphone_dist += t.distance
                iphone_devs[t.uuid] = True
            elif len(t.uuid) < 20 and len(t.uuid) > 0:
                android += 1
                android_dist += t.distance
                android_devs[t.uuid] = True

        self.response.out.write("iphone_dist: %d\n" % iphone_dist)
        self.response.out.write("android_dist: %d\n" % android_dist)
        self.response.out.write("other_dist: %d\n" % other_dist)

        self.response.out.write("iphone_devs: %d\n" % len(iphone_devs))
        self.response.out.write("android_devs: %d\n" % len(android_devs))
        self.response.out.write("other_devs: %d\n" % len(other_devs))

        self.response.out.write('{"android":%d, "iphone":%d, "other":%d}' % (android, iphone, other))

class Kml(webapp.RequestHandler):
    def get(self):
        tracks = Track.get_all(self.request.get('offset'))

        self.response.out.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\
<kml xmlns=\"http://www.opengis.net/kml/2.2\">\
<Document>")

        dec = json.JSONDecoder()
        for t in tracks:
            if t.raw is None:
                continue
                
            if '-' in t.uuid:
                continue

            if len(t.uuid) == 40:
                type = 'iphone'
            elif len(t.uuid) < 20 and len(t.uuid) > 0:
                type = 'android'
            else:
                logging.critical('ehj')

            self.response.out.write("<Placemark><name>0</name><ExtendedData><Data name=\"type\"><displayName>type</displayName><value>%s</value>" % type+
                                    "</Data></ExtendedData><LineString><coordinates>" )

            data = dec.decode(t.raw)
            logging.debug("%s", t.uuid)
            for p in data['track']:
                self.response.out.write("%f,%f\n" % (p['long'], p['lat']))

            self.response.out.write("</coordinates></LineString></PlaceMark>")
            
        self.response.out.write("</Document></kml>")



application = webapp.WSGIApplication(
                                     [('/upload', Upload),
                                      ('/stats/ai', AndroidIphone),
                                      ('/stats/kml', Kml),
                                      ('/stats', Stats)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
