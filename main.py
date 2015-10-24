#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

project = 'BibYAML'
url = 'https://github.com/biomadeira/bibyaml'
author = 'F. Madeira'
date = 'July, 2012'
version = 'beta'
license = 'See License on https://github.com/biomadeira/bibyaml'

import os
import simplejson
import webapp2
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


default_bibtex = """
@Article{journals/aim/Sloman99,
  title =	"Review of Affective Computing",
  author =	"Aaron Sloman",
  journal =	"AI Magazine",
  year = 	"1999",
  number =	"1",
  volume =	"20",
  url =	"http://dblp.uni-trier.de/db/journals/aim/aim20.html#Sloman99",
  pages =	"127--133",
}

@Book{picard:1997a,
  author =	"Rosalind W. Picard",
  title =	"Affective Computing",
  publisher =	"The {MIT} Press",
  year = 	"1997",
  address =	"Cambridge, Massachusetts",
  ISBN = 	"0-262-16170-2",
}

@Article{journals/aim/Picard99,
  title =	"Response to Sloman's Review of Affective Computing",
  author =	"Rosalind W. Picard",
  journal =	"AI Magazine",
  year = 	"1999",
  number =	"1",
  volume =	"20",
  url =	"http://dblp.uni-trier.de/db/journals/aim/aim20.html#Picard99",
  pages =	"134--137",
}
"""

def bibtex2bibyaml(entry):
    "The most naive BibTeX parser in the world."
    ref = ""
    try:
        new_entry = ''	
        for char in entry:
            if '\n' not in char:
                new_entry += char			
        bib = new_entry.split(',')
        type = bib[0].split('{')
        type = type[0]
        type = type.rstrip()
        type = type.lstrip()
        name = bib[0].split('{')
        name = name[1].rstrip('\n')
        name = name.rstrip()
        name = name.lstrip()
        ref = "%s:\n    - name: %s\n" %(type, name )
        for i in range(1,len(bib)-1):
            value = bib[i].split('=')
            left = value[0].lstrip()
            left = left.rstrip()
            right = value[1].rstrip(',')
            right = right.lstrip()
            right = right.rstrip('}')
            right = right.strip('  {}""')
            right = right.rstrip()
            right = right.lstrip()
            ref += "    %s: %s\n" %(left, right)
    except: pass
    return ref

def getOutput(bib) :
    try :
        out = ""
        entries = bib.split('@')
        entries.pop(0)
        for entry in entries:
            processed = bibtex2bibyaml(entry)
            out += processed + '\n'
        return out
    except Exception, why :
        return "ERROR:\n\n" + str(why)

class MainHandler(webapp.RequestHandler):
    def get(self):
        bib = self.request.get("bibtex", default_bibtex)
        output = getOutput(bib)

        template_values = {}
        template_values['output'] = output
        template_values['bibtex'] = bib

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

    def post(self) :
        return self.get()

class AjaxHandler(webapp.RequestHandler):
    def get(self):
        bib = self.request.get("bibtex")
        output = getOutput(bib)
        
        response = simplejson.dumps(output)
        cb = self.request.get("callback")
        if cb :
            response = cb + "(" + response + ")"

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(response)

    def post(self) :
        return self.get()


application = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/ajax', AjaxHandler),
], debug=True)
