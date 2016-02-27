# Copyright 2015, Google, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable
# law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and
# limitations under the License.

"""Try Google AppEngine Now Sample webapp2 Application."""
import webapp2
import jinja2
import json
import os
from yelp import *

# Template Directories
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

# MainHandlerClass
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    # Display landing page on load
    def get(self):
        self.render("index.html")

class IthacaPage(Handler):
	# If GET, view ithaca map
    def get(self):
        self.render("ithacamap.html")

class NYCPage(Handler):
    # If GET, view NYC map
    def get(self):
        self.render("nycmap.html")

class IthacaHandler(Handler):
    # Get all businesses
    def get(self):
        lat_lng_array = []
        with open('mapdata/ithaca_lat_lng.txt') as text_file:
            content = text_file.readlines()
        for x in content:
            lat_lng_array.append(eval(x))
        self.write(json.dumps(lat_lng_array))

class NYCHandler(Handler):
    # Get all businesses
    def get(self):
        lat_lng_array = []
        with open('mapdata/nyc_lat_lng.txt') as text_file:
            content = text_file.readlines()
        for x in content:
            lat_lng_array.append(eval(x))
        self.write(json.dumps(lat_lng_array))

def handle_404(request, response, exception):
    """Return a custom 404 error."""
    response.write('Sorry, nothing at this URL.')
    response.set_status(404)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/ithaca', IthacaPage),
    ('/nyc', NYCPage),
    ('/ithacadata', IthacaHandler),
    ('/nycdata', NYCHandler)
], debug=True)
app.error_handlers[404] = handle_404
