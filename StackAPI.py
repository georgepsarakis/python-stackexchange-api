from itertools import imap, chain
from hashlib import md5
from time import time, sleep
from functools import partial
import requests
try:
  import simplejson as json
except ImportError:
  import json
try:
  from bs4 import BeautifulSoup as bs
except ImportError:
  bs = None

class StackObject(dict):
  def __init__(self, attrs, **kwargs):
    if 'fields' in kwargs and kwargs['fields']:
      attrs = dict([ (field, attrs[field]) for field in kwargs['fields'] if field in attrs ])
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
  AUTHENTICATED = [
  ]
  def __init__(self, **kwargs):
    self.AUTH = {}
    self.SORT = {}
    if "site" in kwargs:
      self.SITE = kwargs['site']  
    self.set_auth(**kwargs)
    self.HAS_MORE = {}
    self.BACKOFF = {}
    self.__PARAMS = {}
    self.IDS = []
    self.LAST_ERROR = {}

  @staticmethod 
  def objectify(item, **kwargs):
    fields = StackAPI.getdefault(kwargs, 'fields', ())
    for k, v in item.iteritems():
      if isinstance(v, dict):
        item[k] = StackAPI.objectify(v, fields=fields)
    return StackObject(item, fields=fields)      
  
  @staticmethod
  def getdefault(obj, key, default=None):
    try:
      return obj[key]
    except KeyError:
      return default
  
  @staticmethod
  def setdefault(obj, key, default=None):
    try:
      obj[key]
    except KeyError:
      obj[key] = default

  def set_auth(self, **kwargs):
    if "key" in kwargs:
      self.AUTH["key"] = kwargs["key"]
    if "token" in kwargs:
      self.AUTH["access_token"] = kwargs["token"]

  def set_param(self, key, value):
    self.__PARAMS[key] = value
      
  def get_param(self, key):
    return StackAPI.getdefault(self.__PARAMS, key)

  def get_request_signature(self, url, params):
    return md5(url + str(params)).hexdigest()

  def fetch(self, url, **params):
    fields = StackAPI.getdefault(params, 'fields', ())   
    if url in self.BACKOFF:
      delay = time() - self.BACKOFF[url]
      if delay > 0.:
        sleep(delay)
    StackAPI.setdefault(params, 'site', self.SITE)
    R = requests.get(url, params=params)    
    R = json.loads(R.content)
    if 'error_id' in R:
      self.LAST_ERROR = StackAPI.objectify(R)
      return []
    else:
      self.QUOTA = R['quota_remaining']
      self.QUOTA_MAX = R['quota_max']
      self.HAS_MORE[self.get_request_signature(url, params)] = R['has_more']
      self.BACKOFF[url] = time() + StackAPI.getdefault(R, 'backoff', self.DELAY)
      if fields:
        objectify = partial(StackAPI.objectify, fields=fields)
      else:
        objectify = StackAPI.objectify
      return imap(objectify, R['items'])
  
  def url_endpoint(self, *args):
    if self.IDS:
      args = [ ';'.join(self.IDS) ]
      args.extend(args)
      self.IDS = []
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
    if 'ids' in params:
      self.IDS = params['ids']
      del params['ids']
    StackAPI.setdefault(params, 'page', 1)
    if call in [ 'posts', 'questions', 'answers' ]:
      StackAPI.setdefault(params, 'sort', 'activity')
      StackAPI.setdefault(params, 'order', 'desc')
    elif call in [ 'comments' ]:
      StackAPI.setdefault(params, 'sort', 'creation')
      StackAPI.setdefault(params, 'order', 'desc')
  
  def get_globals(self, *args):
    return chain(*[ self.FILTERS[key] for key in args ])

  def comments(self, **params):
    params['method'] = 'comments'
    return self.posts(**params)

  def answers(self, **params):
    params['method'] = 'answers'
    return self.posts(**params)

  def questions(self, **params):
    params['method'] = 'questions'
    return self.posts(**params)

  def posts(self, **params):
    self.parameterize('posts', params)
    method = StackAPI.getdefault(params, 'method', 'posts')
    endpoint = self.url_endpoint(method)
    while self.advance(endpoint, params):  
      r = self.api_call(method, **params)
      params['page'] += 1
      yield r
  
  def ids(self, id_list):
    self.IDS = id_list
    return self

  def order(self, field="activity", order="desc"):
    self.SORT = {
      "sort"  : field,
      "order" : order,
    }
    return self
  
  def last_error(self):
    return self.LAST_ERROR

  def advance(self, endpoint, params):
    signature = self.get_request_signature(endpoint, params)    
    if not signature in self.HAS_MORE:
      return True
    else:
      return self.HAS_MORE[signature]

 
