import datetime
import logging
import time
import random
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json
from counter import Counter
import math
from google.appengine.api import memcache

class Track(db.Model):
    uuid = db.StringProperty()
    uploadtime = db.DateTimeProperty()
    distance = db.IntegerProperty()
    raw = db.TextProperty()
    avg_dist = db.FloatProperty()
    avg_acc = db.FloatProperty()
    max_diff = db.IntegerProperty()
    nr = db.IntegerProperty()
    ok = db.BooleanProperty()

#    @staticmethod
#    def get_all(offset):
#        return db.GqlQuery('SELECT * FROM Track LIMIT 100 OFFSET %s' % offset)

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
#        if not dist:
#            dist = Counter(key_name='distance', value=0)
#            dist.put()
        totaldistance = dist.value

        number = Counter.get_by_key_name('number')
#        if not number:
#            number = Counter(key_name='number', value=0)
#            number.put()
        totaltracks = number.value

        my_n = 0
        my_m = 0
        if self.request.get('uid'):
            trk_q = db.GqlQuery("SELECT * FROM Track WHERE uuid='%s'" % self.request.get('uid'))
            trks = trk_q.fetch(1000)
            if not trks:
                logging.warn('no tracks for this uid (yet)')

            for trk in trks:
                my_m += trk.distance
                my_n += 1

            self.response.out.write('{"totalDistance":%d, "totalTracks":%d, "myDistance":%d, "myTracks":%d}' % (totaldistance, totaltracks, my_m, my_n))


        else:
            self.response.out.write('{"totalDistance":%d, "totalTracks":%d}' % (totaldistance, totaltracks))

class AndroidIphone(webapp.RequestHandler):
    def get(self):
        tracks = Track.all()
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
#            if t.uploadtime < datetime.datetime(2011,6,28):
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
        dump_tracks = False
        if self.request.get('ids'):
            tracks = Track.get_by_id([int(id) for id in self.request.get('ids').split(',')])
        elif self.request.get('cursor'):
            tracks = Track.all()
            tracks.filter("ok =", True)

            if self.request.get('cursor') != 'start':
                tracks.with_cursor(memcache.get('cursor'))

            ttt = tracks.fetch(limit=20)
            logging.info("New cursor: " + tracks.cursor())
            memcache.set('cursor', tracks.cursor())
            tracks = ttt
        else:
            """offset=123"""
            tracks = Track.all()
            tracks.filter("nr >", 40)
            if self.request.get('limit'):
                limit = int(self.request.get('limit'))
                dump_tracks = True
            else:
                limit = 100

            offset = int(self.request.get('offset'))
            ttt = tracks.fetch(limit=limit, offset=offset)
            logging.info("New cursor: " + tracks.cursor())
            tracks = ttt

        count = 0
        dec = json.JSONDecoder()
        for t in tracks:
            if t.raw is None:
                logging.critical("Track illegal %d" % t.key().id())
                continue

            if not t.max_diff:
                logging.critical("max diff not found [%d]" % t.key().id())
                continue

#            if not t.avg_dist or not t.avg_acc:
#                continue
#
            if '-' in t.uuid:
                logging.critical("Uid illegal %d" % t.key().id())
                continue

#            if len(t.uuid) == 40:
#                type = 'iphone'
#            elif len(t.uuid) < 20 and len(t.uuid) > 0:
#                type = 'android'
#            else:
#                logging.critical('ehj')

            self.response.out.write("<Placemark><ExtendedData>" +
                                    "<Data name=\"avg_acc\"><displayName>avg_acc</displayName><value>%f</value></Data>" % t.avg_acc +
                                    "<Data name=\"avg_dist\"><displayName>avg_dist</displayName><value>%f</value></Data>" % t.avg_dist +
                                    "<Data name=\"max_diff\"><displayName>max_diff</displayName><value>%d</value></Data>" % t.max_diff +
                                    "</ExtendedData><LineString><coordinates>" )

            count += 1
            if dump_tracks:
                if t.avg_dist > 100 or t.max_diff > 100 or t.avg_acc > 50:
                    logging.debug("Track [%d] - avg_dist=%f, max_diff=%d, avg_acc=%f" % (t.key().id(), t.avg_dist, t.max_diff, t.avg_acc))

            data = dec.decode(t.raw)
            for p in data['track']:
                self.response.out.write("%f,%f\n" % (p['long'], p['lat']))

            self.response.out.write("</coordinates></LineString></Placemark>\n")
            
        logging.info("processed %d tracks" % count)

class Filter(webapp.RequestHandler):
    def get(self):
        tracks = Track.get_all(self.request.get('offset'))

        dec = json.JSONDecoder()
        for t in tracks:
            if t.raw is None:
                continue

            if '-' in t.uuid:
                continue

            data = dec.decode(t.raw)

            dist = 0
            prev_lat = None
            prev_lng = None
            max_diff = 0.0
            nr = 0

            sum_acc = 0

            for p in data['track']:
                if p['acc'] > 30:
                    continue

                sum_acc += p['acc']
                lat = p['lat']; lng = p['long']
                if prev_lat and prev_lng:
                    lat_diff = math.fabs(lat-prev_lat)
                    lng_diff = math.fabs(lng-prev_lng)
                    diff = math.sqrt((lat_diff * 111111)**2 + (lng_diff*75500)**2)
                    if diff > max_diff:
                        max_diff = diff

                    nr += 1
                    dist += diff

                prev_lat = lat
                prev_lng = lng

            if not nr:
                continue
                
            avg_acc = sum_acc / float(nr)
            avg_dist = float(dist) / float(nr)

            t.avg_dist = avg_dist
            t.avg_acc = float(avg_acc)
            t.nr = nr
            t.put()

            if max_diff > 200:
                self.response.out.write("[%d] Track distance: %d nr: %d - our distance: %d - max diff: %f - avg acc: %f - avg dist: %f\n" % (t.key().id(), data['distance'], nr, dist, max_diff, avg_acc, avg_dist))


class OldTracks(webapp.RequestHandler):
    def get(self):
        tracks = Track.all()
        for t in tracks:
            if not t.raw:
                logging.info("Checking track %d" % t.key().id())
                q = db.GqlQuery("SELECT * FROM Point WHERE ANCESTOR IS :1", t.key())

                le_traq = []
                for pt in q:
                    unixtime = int(time.mktime(pt.ts.timetuple()))
                    le_traq.append({"ts":unixtime, "lat":pt.lat, "long":pt.lng, "acc":pt.acc})

                logging.info("Nr of points: %d" % len(le_traq))
                self.response.out.write("nr of points: %d\n" % len(le_traq))

                if len(le_traq) < 5:
                    logging.info("Very short route. deleted.")
                    self.response.out.write('deleted track %d' % t.key().id())
                    t.delete()
                    return

                logging.info("encoding...")
                encoder = json.JSONEncoder()
                t.raw = encoder.encode({"track": le_traq, "distance":0, "uuid":t.uuid})

                logging.info("Ok, writing back track")
                t.put()

                self.response.out.write('Track %d updated' %  t.key().id())
                return
                
        self.response.out.write('FIN')


class QR(webapp.RequestHandler):
    def get(self):
        useragent = self.request.headers['User-Agent']
        if 'Android' in useragent:
            loc = "market://search?q=pname:hu.budapestcycletrack"
        elif 'iPhone' in useragent or 'Darwin' in useragent:
            loc = "http://itunes.apple.com/hu/app/budapest-cycle-tracker/id433400907?mt=8"
        else:
            loc = "http://www.urbancyclr.com"

        self.response.headers['Location'] = loc
        self.response.set_status(301)
        



class Competition(webapp.RequestHandler):
    def get(self):
        tracks = Track.all()
        tracks.filter("uploadtime >", datetime.datetime(2011,7,5))
        tracks.filter("uploadtime <", datetime.datetime(2011,7,12))
        tracks.filter("ok =", True)
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

        self.response.out.write("Tavolsag:\niphone: %d\n" % iphone_dist)
        self.response.out.write("android_dist: %d\n" % android_dist)
        self.response.out.write("-------\nEszkozok:\niphone: %d\n" % len(iphone_devs))
        self.response.out.write("android: %d\n" % len(android_devs))
        self.response.out.write("------\ntracks:\nandroid: %d\n" % android)
        self.response.out.write("iphone: %d\n" % iphone)


application = webapp.WSGIApplication(
                                     [('/upload', Upload),
                                      ('/stats/ai', AndroidIphone),
                                      ('/stats/compo', Competition),
                                      ('/stats/kml', Kml),
                                      ('/stats/filter', Filter),
                                      ('/hello_old_tracks', OldTracks),
                                      ('/qr', QR),
                                      ('/stats', Stats)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
