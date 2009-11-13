from google.appengine.api import memcache
from model import *
from google.appengine.api import memcache
import logging

logging.getLogger().setLevel(logging.DEBUG)

class ModelHelpers():
    @staticmethod 
    def add_user(user):
        u = User(key_name=str(user))
        u.account = user
        u.put()
        # loads the user in the memcache
        memcache.set(str(user),[])
        
        return u
        # force the sequence
        # returns the list keys (from myspaceapps)
        # now retrieve all apps keys
        # for this user an add them to memcache
        # lista = [x for x in user.applications()]
        # memcache.set(user,lista)

    # deletes the user from the DB and from memcache
    @staticmethod
    def delete_user(userobj):
        memcache.set(str(userobj.key()),None)
        db.delete(userobj)
        

    @staticmethod
    def delete_application_from(userobj,app):
        # clear from the many-to-many in db
        appu = UserMyspace.search_by_appuser(app,userobj)
        logging.error("OK, object ready to delete")
        logging.error(str(appu))
        db.delete(appu)
        # reload apps in cache
        userobj.applications_reload()
        # clear from the memcache
        #raise 'Not implemented yet'
    
    @staticmethod
    def search_user(user):
        user = User.get_by_key_name(str(user))
        if user:
            user.applications()
        return user

    @staticmethod
    def search_application(link):
        app = Myspaceapp.get_by_key_name(link)
        if app:
            return app
        else:
            return None

    @staticmethod
    def add_application(link):
        app = Myspaceapp(key_name=link)
        app.on_load(link)
        app.put()
        return app
        # do not put it in memcache
        # only when a user adds - maybe change this in the future
    
        
