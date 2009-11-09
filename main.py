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

from model import *
from wrappers import *    
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

  @require_user
  def unregister_command(self,message=None):
    db.delete(self.user)
    message.reply("You've been unregistered")

  @require_user
  @require_valid_number
  def forget_command(self,message=None):
    # force the lazy sequence
    list_apps = [x for x in self.user.applications()]
    # check if index is inbounds 
    if self.index >= len(list_apps) or self.index < 0:
      message.reply("That number is not valid!!")
    else:
      # the app to remove from users <=> apps list
      app_rem = list_apps[self.index]
      # the link to remove from the many-to-many table
      app_connection = UserMyspace.search_by_myspace(app_rem)
      db.delete(app_connection)
      message.reply("You've stopped tracking: " + str(app_rem.link))

  @require_user
  @require_link
  def track_command(self,message=None):
    try:
      app = Myspaceapp.search_by_link(self.content)
      if len(filter(lambda x: x.link == self.content,self.user.applications())) > 0 :
        # application already in user list!!
        message.reply("This application was already in your list!!")
      else:
        # if not, create it
        if not app:
          app = Myspaceapp()
          app.on_load(self.content)
          app.put()
        # create the necessary connection to the user
        appuser = UserMyspace()
        appuser.user = self.user
        appuser.application = app
        appuser.put()
        message.reply("Saved " + self.content + " in the database")
    except Exception, inst:
      e = Error()
      e.msg = str(inst)
      e.put()
      message.reply("That link is not valid!!")
    
  @require_user
  def list_command(self,message=None):
    list_links = "List of Links:\n"
    counter = 1
    for app in self.user.applications():
      app.update_nusers()
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
