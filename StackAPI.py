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
      attrs = StackAPI.field_filter(attrs, fields=kwargs['fields'])
    super(StackObject, self).__init__(attrs.items())
    self.__dict__.update(attrs) 

class StackAPI(object):
  API_BASEURL = 'https://api.stackexchange.com/2.1'
  SITE = "stackoverflow"
  QUOTA = None
  QUOTA_MAX = None
  DELAY = 0.5
  SORTING = {
    "posts"  : [ "activity", "creation", "votes" ],
    "badges" : [ "rank", "name", "type" ],
    "tags"   : [ "popular", "activity", "name" ],
  }
  FILTERS = {
    "global" : [
      "page", "pagesize",
    ],
    "posts" : [
      "fromdate", "todate", "min", "max", "order", "sort",
    ]
  }
  API_METHODS = {
    "posts"     : True,
    "answers"   : True,
    "questions" : True,
    "badges"    : True,
    "comments"  : True,
    "tags"      : True,
    "users"     : True,
    "errors"    : True,
    "sites"     : True,
    "info"      : True,
  }
  NO_PAGINATION_METHODS = {
    "info"   : True,
    "sites"  : True,
    "errors" : True,
  }
  def __init__(self, **kwargs):
    self.SITE = StackAPI.getdefault(kwargs, 'site', self.SITE)
    self.__PARAMS = {}
    self.AUTH = {}
    self.SORT = {}
    self.HAS_MORE = {}
    self.BACKOFF = {}
    self.IDS = []
    self.LAST_ERROR = {}
    self.LAST_URL = None
    self.RESPONSE_FORMAT = "object"
    self.set_auth(**kwargs)
  
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

  @staticmethod
  def field_filter(obj, **kwargs):
    if not 'fields' in kwargs:
      return obj    
    fields = kwargs['fields']
    if fields is None or not isinstance(fields, list):
      return obj
    else:
      return dict([ (field, obj[field]) for field in fields if field in obj ])

  def __getattr__(self, name):    
    if name in self.API_METHODS:
      def wrapper(*args, **kwargs):
        kwargs['method'] = name
        return self.response(**kwargs)
      return wrapper
    else:
      return None

  def set_response_format(self, response_format):
    if response_format in [ "json", "object" ]:
      self.RESPONSE_FORMAT = response_format
      return True
    else:
      return False

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
    if 'fields' in params:
      del params['fields']
    if url in self.BACKOFF:
      delay = self.BACKOFF[url] - time()
      if delay > 0.:
        sleep(delay)
    StackAPI.setdefault(params, 'site', self.SITE)
    R = requests.get(url, params=params)
    self.LAST_URL = R.url
    R = json.loads(R.content)
    if 'error_id' in R:
      R["url"] = self.LAST_URL
      if self.RESPONSE_FORMAT == "object":
        self.LAST_ERROR = StackAPI.objectify(R)
      elif self.RESPONSE_FORMAT == "json":
        self.LAST_ERROR = R
      return []
    else:
      self.QUOTA = R['quota_remaining']
      self.QUOTA_MAX = R['quota_max']
      self.HAS_MORE[self.get_request_signature(url, params)] = R['has_more']
      self.BACKOFF[url] = time() + StackAPI.getdefault(R, 'backoff', self.DELAY)
      if self.RESPONSE_FORMAT == "object":
        if fields:
          objectify = partial(StackAPI.objectify, fields=fields)
        else:
          objectify = StackAPI.objectify
        return imap(objectify, R['items'])
      elif self.RESPONSE_FORMAT == "json":
        if fields:
          field_filter = partial(StackAPI.field_filter, fields=fields)
        else:
          field_filter = StackAPI.field_filter 
        return imap(field_filter, R['items'])
  
  def url_endpoint(self, *args):
    return '%s/%s' % (self.API_BASEURL, '/'.join(args))
  
  def api_call(self, *endpoint, **params):
    if self.IDS:
      _ = endpoint[:]
      endpoint = [ _[0], ';'.join(map(str, self.IDS)) ]
      endpoint.extend(_[1:])
      self.IDS = []
    if self.SORT:
      self.SORT = {}
    return self.fetch(self.url_endpoint(*endpoint), **params)
  
  def parameterize(self, call, params):
    StackAPI.setdefault(params, 'page', 1)
    params.update(self.AUTH)
    fields = (field for field in self.get_globals("global", call) if field in self.__PARAMS)
    params.update(dict([ (field, self.__PARAMS[field]) for field in fields ]))
    if 'ids' in params:
      self.IDS = params['ids']
      del params['ids']
    params.update(self.SORT)
    if call in [ 'posts', 'questions', 'answers' ]:
      StackAPI.setdefault(params, 'sort', 'activity')
      StackAPI.setdefault(params, 'order', 'desc')
    elif call in [ 'comments' ]:
      StackAPI.setdefault(params, 'sort', 'creation')
      StackAPI.setdefault(params, 'order', 'desc')
  
  def get_globals(self, *args):
    return chain(*[ self.FILTERS[key] for key in args if key in self.FILTERS ])
  
  def identity(self, obj):
    return obj

  def response(self, **params):    
    pagination = StackAPI.getdefault(params, 'pages', True)
    if 'pages' in params:
      del params['pages']
    data = self.identity
    if 'fields' in params and 'filter' in params:
      if params['filter'] == 'withbody':
        params['fields'].append('body')
    method = StackAPI.getdefault(params, 'method', 'posts')    
    if method in self.NO_PAGINATION_METHODS:
      params['pagesize'] = 100
      pagination = False
      data = next
    url = [ method ]
    if 'url' in params:
      if not isinstance(params['url'], list):
        params['url'] = list(params['url'])
      url.extend(params['url'])
      del params['url']
    self.parameterize(method, params)
    del params['method']
    if pagination:
      return self.response_iterator(url, params)
    else:
      return data(self.api_call(*url, **params))
  
  def response_iterator(self, url, params):
    endpoint = self.url_endpoint(url[0])    
    while self.advance(endpoint, params):  
      r = self.api_call(*url, **params)
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
  
  def advance(self, endpoint, params):
    signature = self.get_request_signature(endpoint, params)    
    if not signature in self.HAS_MORE:
      return True
    else:
      return self.HAS_MORE[signature]

  def last_error(self):
    return self.LAST_ERROR
 
