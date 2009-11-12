from google.appengine.api import memcache
from models import *
from google.appengine.api import memcache

class ModelHelpers():
    

    @staticmethod 
    def add_user(user):
        u = User(key_name=user)
        u.account = user
        u.put()
        # loads the user in the memcache
        memcache.put(user,[])
        
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
        db.delete(userobj)
        memcache.put(userobj,None)

    @staticmethod
    def delete_application_from(useobj,appkey):
        # clear from the many-to-many in db
        # clear from the memcache
        raise 'Not implemented yet'
    
    @staticmethod
    def search_user(user):
        u = memcache.get(user)
        if u:
            return u
        else:
            u = User.get_by_key_name(user)
            if u:
                # load the user and it's apps in the memcache
                u.applications()
                return u
            else:
                return None

    @staticmethod
    def search_application(link):
        

    @staticmethod
    def add_application(memcache,link):
        app = Myspaceapp(key_name=link)
        app.on_load(link)
        app.put()
        # do not put it in memcache
        # only when a user adds - maybe change this in the future
    
        
