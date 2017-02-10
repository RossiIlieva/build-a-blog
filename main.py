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
import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

template_dir=os.path.join(os.path.dirname(__file__),"templates")
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                             autoescape = True)

class Blog(db.Model):
    title=db.StringProperty(required=True)
    new_blog_text=db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)


class Handler(webapp2.RequestHandler):
    """A base handler for the app. The other handlers inherit from this one"""

    def renderError(self,error_code):
        """Sends an HTTP error code and a generic "oops" to the client."""
        self.error(error_code)
        self.response.write("Ooops, something went wrong!")

class ShmindexIndex(Handler):
    """Handles requests to '/'"""

    def get(self):

        self.redirect('/blog')

class Index(Handler):
    """Handles requests coming in to '/blog'"""



    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog "
                            "ORDER BY created DESC LIMIT 5")
        t=jinja_env.get_template("frontpage.html")
        content=t.render(blogs=blogs)
        self.response.write(content)



class NewPost(Handler):

    def get(self):
        t=jinja_env.get_template("newpost.html")
        content=t.render()
        self.response.write(content)





    def post(self):
        title = self.request.get("title")
        new_blog_text = self.request.get("new_blog_text")
        blogs = db.GqlQuery("SELECT * FROM Blog "
                            "ORDER BY created DESC")



        if title and new_blog_text:
            b=Blog(title = title , new_blog_text = new_blog_text)
            b.put()
            #t=jinja_env.get_template("frontpage.html")
            #content=t.render(blogs=blogs)
            #self.response.write(content)
            #k=int(b.key().id())
            #self.response.write(k)
            #self.redirect("/blog/int(b.key().id())")
            blog_perma = b
            t=jinja_env.get_template("permalink.html")
            content=t.render(blog_perma=blog_perma)
            self.response.write(content)



            #self.redirect("/blog")
        else:
            error="Title and content, please!"
            t=jinja_env.get_template("newpost.html")
            content=t.render(title=title, new_blog_text=new_blog_text,error=error)
            self.response.write(content)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):

        blog_perma = Blog.get_by_id(int(id))
        t=jinja_env.get_template("permalink.html")
        content=t.render(blog_perma=blog_perma)
        self.response.write(content)





app = webapp2.WSGIApplication([
    ('/', ShmindexIndex),
    ('/blog',Index),
    ('/newpost',NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug=True)
