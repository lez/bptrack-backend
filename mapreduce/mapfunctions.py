import time
import logging
from api.encoders import DATE_FORMAT
from mapreduce import operation as op
from google.appengine.ext import db
from django.utils import simplejson as json

def mr_convert_to_raw(track):
    """get the Points and convert to Track.raw"""
    if not track.raw:
        logging.info('going for Track id=' + str(track.key().id()))

        pts_query = db.gqlQuery("SELECT * FROM Point WHERE ANCESTOR IS :1 ORDER BY 'ts'", track.key())
        pts = pts_query.all()

        logging.info("track has %d points" % pts.count())

        if pts.count() < 2:
            logging.info("Very short route. Should be deleted.")
            return

        le_traq = []
        for pt in pts:
            unixtime = int(time.mktime(pt.ts.timetuple()))
            le_traq.append({"ts":unixtime, "lat":pt.lat, "long":pt.lng, "acc":pt.acc})

        logging.info("encoding...")
        encoder = json.JSONEncoder()
        track.raw = encoder.encode({"track": le_traq, "distance":0, "uuid":track.uuid})

        logging.info("Ok, writing back track")
        yield op.db.Put(track)
