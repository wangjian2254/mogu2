#coding=utf-8
#
__author__ = u'王健'
#import os,webapp2
import os,webapp2,jinja2
#from django.template import loader
from setting import TEMPLATE_DIR
#from google.appengine.ext.webapp import template


class Page(webapp2.RequestHandler):
    def render(self, template_file, template_value):
        jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
        template = jinja_environment.get_template(template_file)
        self.response.out.write(template.render(template_value))

#        path = os.path.join(TEMPLATE_DIR, template_file)
#        self.response.out.write(template.render(path,template_value))
#