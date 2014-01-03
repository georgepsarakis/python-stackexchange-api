#!/usr/bin/python
import requests
try:
  import simplejson as json
except ImportError:
  import json
from time import time, sleep
from bs4 import BeautifulSoup as bs
from itertools import imap, chain
from hashlib import md5

class StackObject(dict):
  def __init__(self, attrs):
    super(StackObject, self).__init__(attrs.items())
    self.__dict__.update(attrs) 

class StackAPI(object):
  API_BASEURL = 'https://api.stackexchange.com/2.1'
  CONTENT_SELECTORS = { 
			'question' : "div#question div.post-text",
			'answer'   : "div#answer-%([post_id)d div.post-text",
			'comment'  : "div#comment-%(post_id)d div.comment-copy"
		    }      
  SITE = "stackoverflow"
  QUOTA = None
  QUOTA_MAX = None
  DELAY = 0.5
  SORTING = [ 
    "activity", "creation", "votes" 
    ]
  FILTERS = {
    "global" : [
      "page", "pagesize",
    ],
    "posts" : [
      "fromdate", "todate", "min", "max", "order", "sort",
    ]
  }
  def __init__(self, **kwargs):
    self.AUTH = {}
    if "site" in kwargs:
      self.SITE = kwargs['site']  
    self.set_auth(**kwargs)
    self.HAS_MORE = {}
    self.BACKOFF = {}
    self.__PARAMS = {}

  @staticmethod 
  def objectify(item):
    for k, v in item.iteritems():
      if isinstance(v, dict):
        item[k] = StackAPI.objectify(v)
    return StackObject(item)      

  def set_auth(self, **kwargs):
    if "key" in kwargs:
      self.AUTH["key"] = kwargs["key"]
    if "token" in kwargs:
      self.AUTH["access_token"] = kwargs["token"]

  def set_param(self, key, value):
    self.__PARAMS[key] = value
      
  def get_param(self, key):
    return self.getdefault(self.__PARAMS, key)

  def get_request_signature(self, url, params):
    return md5(url + str(params)).hexdigest()

  def fetch(self, url, **params):
    if url in self.BACKOFF:
      delay = time() - self.BACKOFF[url]
      if delay > 0.:
        sleep(delay)
    self.setdefault(params, 'site', self.SITE)
    R = requests.get(url, params=params)    
    R = json.loads(R.content)
    if 'error_id' in R:
      self.LAST_ERROR = StackAPI.objectify(R)
      return []
    else:
      self.QUOTA = R['quota_remaining']
      self.QUOTA_MAX = R['quota_max']
      self.HAS_MORE[self.get_request_signature(url, params)] = R['has_more']
      self.BACKOFF[url] = time() + self.getdefault(R, 'backoff', self.DELAY)
      return imap(StackAPI.objectify, R['items'])
  
  def url_endpoint(self, *args):
    return '%s/%s' % (self.API_BASEURL, '/'.join(args))
  
  def api_call(self, *endpoint, **params):
    return self.fetch(self.url_endpoint(*endpoint), **params)

  def info(self, site=None):
    params = {}
    if not site is None:
      params['site'] = site
    return next(self.api_call('info', **params))
  
  def parameterize(self, call, params):
    fields = (field for field in self.get_globals("global", call) if field in self.__PARAMS)
    params.update(dict([ (field, self.__PARAMS[field]) for field in fields ]))
    if call in [ 'posts', 'questions', 'answers' ]:
      self.setdefault(params, 'page', 1)
      self.setdefault(params, 'sort', 'activity')
      self.setdefault(params, 'order', 'desc')
  
  def get_globals(self, *args):
    return dict(chain([ self.FILTERS[key] for key in args ]))

  def posts(self, **params):
    self.parameterize('posts', params)
    endpoint = self.url_endpoint('posts')
    while self.advance(endpoint, params):  
      r = self.api_call('posts', **params)
      params['page'] += 1
      yield r

  def advance(self, endpoint, params):
    signature = self.get_request_signature(endpoint, params)    
    if not signature in self.HAS_MORE:
      return True
    else:
      return self.HAS_MORE[signature]

  def getdefault(self, obj, key, default=None):
    try:
      return obj[key]
    except KeyError:
      return default

  def setdefault(self, obj, key, default=None):
    try:
      obj[key]
    except KeyError:
      obj[key] = default
      
