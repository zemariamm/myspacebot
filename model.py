from google.appengine.ext import db
from google.appengine.api import users
from datetime import datetime, timedelta
import sys
from bsoup import SoupHelpers

# class Error(db.Model):
#     msg = db.StringProperty()

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

class Myspaceapp(db.Model, SoupHelpers ):
  link = db.LinkProperty()
  name = db.StringProperty()
  nusers = db.IntegerProperty()
  last_update = db.DateTimeProperty(auto_now_add=True)

  def on_load(self,link):
      self.link = link
      self.load()
      self.name = self.extract_app_name()
      self.nusers = self.extract_nusers()
      
  def update_nusers(self):
      update_after = timedelta(minutes=1)
      current = datetime.now()
      elapsed = current - self.last_update
      if elapsed > update_after:
          #self.url = self.link
          self.load()
          self.nusers = self.extract_nusers()
          self.last_update = current
      

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
