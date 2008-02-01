# FlickrClient
# Copyright (c) 2004 Michele Campeotto

import xmltramp
import sys

from urllib import urlencode


HOST = 'http://flickr.com'
PATH = '/services/rest/'
API_KEY = '202674dc858dc950b7589847eb7754ab'


class FlickrError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
    
    def __str__(self):
        return 'Flickr Error %s: %s' % (self.code, self.message)


class Photo(object):
    def __init__(self, client, id, secret):
        self.photo = client.flickr_photos_getInfo(photo_id=id, secret=secret)
        self.description = self.getDescription()
        self.tags = self.getTags()
        self.urls = self.getURLs()
        # self.comments = self.getComments()
        self.title = self.getTitle()

    def getDescription(self):
        return unicode(self.photo.description)

    def getTags(self):
        result = []
        for tag in self.photo.tags:
            result.append(tag[0])
        return result

    def getURLs(self):
        result = []
        for url in self.photo.urls:
            result.append(url[0])
        return result

    # def getComments(self):
    #    return self.photo.comments[0]

    def getTitle(self):
        return unicode(self.photo.title)


class FlickrClient:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def __getattr__(self, method):
        def method(_self=self, _method=method, **params):
            _method = _method.replace("_", ".")
            url = HOST + PATH + "?method=%s&%s&api_key=%s" % \
                    (_method, urlencode(params), self.api_key)
            try:
                    rsp = xmltramp.load(url)
            except:
                    return None
            return _self._parseResponse(rsp)
        return method

    def _parseResponse(self, rsp):
        if rsp('stat') == 'fail':
            raise FlickrError(rsp.err('code'), rsp.err('msg'))
        
        try:
                return rsp[0]
        except:
                return None

    def getPhotoInfo(self, id, secret):
        return Photo(self, id, secret)

user = None
photoSets = None
if __name__ == '__main__':
    USER_ID = '51035543396@N01'
    
    client = FlickrClient(API_KEY)
    
    person = client.flickr_people_getInfo(user_id=USER_ID)
    photoSets = client.flickr_photosets_getList(user_id=USER_ID)
    
    print person.username, "has", len(photoSets), "photosets:",
    print ', '.join([str(set.title) for set in photoSets])
    
    photo = client.getPhotoInfo('280055655', 'eabe08dad5')
    # photo = client.getPhotoInfo('1046516447', 'e9969afba5')
    print
    print u'Title:', photo.title
    print u'Description:', photo.description
    print u'URLs:', photo.urls
    print u'Tags:', photo.tags
