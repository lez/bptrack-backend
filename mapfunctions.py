import time
import logging
from mapreduce import operation as op
from django.utils import simplejson as json
import math

def mr_convert_to_raw(track):

    if track.avg_acc and track.avg_acc < 45 and track.max_diff and track.max_diff < 300:
        track.ok = True
    else:
        track.ok = False

    yield op.db.Put(track)



# ===============================
#    dec = json.JSONDecoder()
#    data = dec.decode(track.raw)
#
#    nr = 0
#    dist = 0
#    sum_acc = 0.0
#    prev_lat = None
#    prev_lng = None
#    max_diff = 0.0
#
#    for p in data['track']:
#        sum_acc += p['acc']
#        lat = p['lat']; lng = p['long']
#        if prev_lat and prev_lng:
#            lat_diff = math.fabs(lat-prev_lat)
#            lng_diff = math.fabs(lng-prev_lng)
#            diff = math.sqrt((lat_diff * 111111)**2 + (lng_diff*75500)**2)
#            if diff > max_diff:
#                max_diff = diff
#
#            nr += 1
#            dist += diff
#
#        prev_lat = lat
#        prev_lng = lng
#
#    track.nr = nr
#
#    if nr > 0:
#        track.avg_acc = float(sum_acc) / nr
#        track.avg_dist = float(dist) / nr
#        track.max_diff = int(max_diff)
#        logging.info("Enabled track w %d points: [%d]" % (track.nr, track.key().id()))
#
#    else:
#        logging.info("Disabled track %d" % track.key().id())
#
#    yield op.db.Put(track)

