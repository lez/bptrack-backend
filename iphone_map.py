from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from mako.template import Template

class Map(webapp.RequestHandler):
    def post(self):
               
        lat = self.request.get('lat')
        if not lat:
            lat = 47.48414889179508

        lng = self.request.get('lng')
        if not lng:
            lng = 19.059476852416992

        template = Template(filename="iphone_map.html",
                            input_encoding='utf8',
                            output_encoding='utf8')
        

        output = template.render(lat=lat,lng=lng)
        self.response.out.write(output)


    def get(self):
        lat = 47.48414889179508
        lng = 19.059476852416992

        template = Template(filename="iphone_map.html",
                            input_encoding='utf8',
                            output_encoding='utf8')
        
        output = template.render(lat=lat,lng=lng)
        self.response.out.write(output)

       

application = webapp.WSGIApplication(
                                     [('/iphone_map', Map)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
