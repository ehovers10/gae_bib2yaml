#!/usr/bin/env python
#
# Copyright 2012 Fabio Madeira.
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

project = 'Bib2YAML'
url = 'https://github.com/biomadeira/gae_bib2yaml'
author = 'F. Madeira'
created = 'July, 2012'
version = 'beta'
license = 'See License @url'

import os
import simplejson
import json
import webapp2
import wsgiref.handlers
from bibpy.bib import Parser
from collections import OrderedDict
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


default_bibtex = """
@article{ berger2003,
    author = {Berger, Jean and Barkaoui, Mohamed},
    issn = {0160-5682},
    journal = {Journal of the Operational Research Society},
    number = {12},
    pages = {1254--1262},
    publisher = {Nature Publishing Group},
    title = {{A new hybrid genetic algorithm for the capacitated vehicle routing problem}},
    url = {http://www.palgrave-journals.com/jors/journal/v54/n12/abs/2601635a.html},
    volume = {54},
    year = {2003}
}

@book{ aaker:1981a,
    author = {David A. Aaker},
    title = {Multivariate Analysis in Marketing},
    edition = {2},
    publisher = {The Scientific Press},
    year = {1981},
    address = {Palo Alto},
    topic = {multivariate-statistics;market-research;}
 }
"""

def output_bibyaml(bib):
    "Outputs BibYAML"
    
    bibyaml = ""
    for ent in bib["items"]:
        head = ent["type"]
        body = ""
        for k in ent:
            value = ent[k]
            try:
                value = value.replace(" ,", ",")
            except AttributeError:
                pass
            if k == "type":
                continue
            if isinstance(ent[k], list):
                for e in ent[k]:
                     value = ", ".join(e.values())
            if isinstance(ent[k], dict):
                value = ", ".join(ent[k].values())

            body += "\t{}: {}\n".format(k, value)
        bibyaml += "{}:\n{}\n".format(head, body)

    return bibyaml


def parse_bibtex(bib):
    "Parses Bibtex with bibpy"
    
    data = Parser(bib)
    data.parse()
    bib = json.loads(data.json(),  object_pairs_hook=OrderedDict)
    print bib
    return bib


class MainHandler(webapp.RequestHandler):
    def get(self):
        bibtex = self.request.get("bibtex", default_bibtex)
        bibjson = parse_bibtex(bibtex)
        bibyaml = output_bibyaml(bibjson)

        template_values = {}
        template_values['output'] = bibyaml
        template_values['bibtex'] = bibtex

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

    def post(self) :
        return self.get()


class AjaxHandler(webapp.RequestHandler):
    def get(self):
        bibtex = self.request.get("bibtex", default_bibtex)
        bibjson = parse_bibtex(bibtex)
        bibyaml = output_bibyaml(bibjson)
        
        response = simplejson.dumps(bibyaml)
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
