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

import wsgiref.handlers
from google.appengine.api import xmpp
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import xmpp_handlers
from google.appengine.ext import db


class User(db.Model):
  account = db.IMProperty()

  def applications(self):
    return (x.application for x in self.usermyspace_set)

  @staticmethod
  def search_by_name(user):
    unames = User.gql("WHERE account = :1", db.IM("xmpp",user))
    lista = [x for x in unames]
    if len(lista) > 0:
      return unames[0]
    else:
      return None

class Myspaceapp(db.Model):
  link = db.LinkProperty()
  name = db.StringProperty()
  nusers = db.IntegerProperty()
  last_update = db.DateTimeProperty(auto_now_add=True)

  def users(self):
    return (x.user for x in self.usermyspace_set)

  @staticmethod
  def search_by_link(link):
    apps = Myspaceapp.gql("WHERE link = :1", db.Link(link))
    # gql is lazy, force the sequence
    lista = [x for x in apps]
    if len(lista) > 0:
      return apps[0]
    else:
      return None
    

class UserMyspace(db.Model):
  user = db.ReferenceProperty(User)
  application = db.ReferenceProperty(Myspaceapp)

  @staticmethod
  def search_by_myspace(app):
    apps = UserMyspace.gql("WHERE application = :1", app.key())
    # gql is lazy, force the sequence
    lista = [x for x in apps]
    if len(lista) > 0:
      return apps[0]
    else:
      return None
    
class MainHandler(webapp.RequestHandler):

  def get(self):
    self.response.out.write('Add botmyspace@appspot.com to your gchat client and start speaking with him')
  
class XMPPHandler(xmpp_handlers.CommandHandler):

  def register_command(self,message=None):
    user = User.search_by_name(message.sender)
    if user:
      #if user is already in the database
      message.reply("You " + str(user.account.address) + " are already registered")
    else:
      # if not, add the user to the DB and send the appropriate msg
      u = User()
      u.account = db.IM("xmpp",message.sender)
      u.put()
      message.reply("Hello " + str(u.account.address) + " you've been registered")

  def unregister_command(self,message=None):
    user = User.search_by_name(message.sender)
    if user:
      db.delete(user)
    message.reply("You've been unregistered")

  def forget_command(self,message=None):
    user = User.search_by_name(message.sender)
    if not user:
      message.reply("You have to register first!!")
    content = message.arg
    try:
      index = int(content)
      # the user send the nth element, not the postion
      index = index - 1
      # force the lazy sequence
      list_apps = [x for x in user.applications()]
      # check if index is inbounds 
      if index >= len(list_apps) or index < 0:
        message.reply("That number is not valid!!")
      else:
        # the app to remove from users <=> apps list
        app_rem = list_apps[index]
        # the link to remove from the many-to-many table
        app_connection = UserMyspace.search_by_myspace(app_rem)
        db.delete(app_connection)
        message.reply("You've stopped tracking: " + str(app_rem.link))
    except Exception:
      message.reply("You must send an integer indexing one element of the list")
        #message.reply("Debug: should never get here")


  def track_command(self,message=None):
    user = User.search_by_name(message.sender)
    content = message.arg
    if not user or not content:
      message.reply("You must register and send a valid message!!")
      # check if app is in the DB
    else:
      try:
        app = Myspaceapp.search_by_link(content)
        if len(filter(lambda x: x.link == content,user.applications())) > 0 :
          # application already in user list!!
          message.reply("This application was already in your list!!")
        else:
          # if not, create it
          if not app:
            app = Myspaceapp()
            app.link = content
            app.name = "test app"
            app.nusers = 0
            app.put()
        # create the necessary connection to the user
          appuser = UserMyspace()
          appuser.user = user
          appuser.application = app
          appuser.put()
          message.reply("Saved " + content + " in the database")
      except:
        message.reply("That link is not valid!!")
    
      
  def list_command(self,message=None):
    user = User.search_by_name(message.sender)
    if not user:
      message.reply("You must register first!!")
    else:
      list_links = "List of Links:\n"
      counter = 1
      for app in user.applications():
        list_links = list_links + str(counter) + ") " + app.name + " users: " + str(app.nusers) + " link: " + str(app.link) + "\n"
        counter = counter + 1
      message.reply(list_links)


  def help_command(self,message=None):
    im_from = db.IM("xmpp", message.sender)
    message.reply("Todo my friend " + str(im_from))


  def unhandled_command(self, message=None):
    message.reply("Unknown command see /help")

application = webapp.WSGIApplication([('/', MainHandler),
                                      ('/_ah/xmpp/message/chat/', XMPPHandler)],
                                     debug=True)
    

def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
