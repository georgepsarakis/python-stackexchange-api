#!/usr/bin/python
from urllib2 import urlopen, Request
from zlib import decompress, error, MAX_WBITS
import lxml.html as parser
from lxml.etree import tostring as htmltext
import json, helper
from helper import *
from time import time
from BeautifulSoup import BeautifulSoup as bsoup

class stackAPI:
    API_URL = 'https://api.stackexchange.com/2.1'
    ANSWERS_URL = API_URL + '/questions/%(ids)s/answers/?order=desc&sort=activity&site=stackoverflow'
    ANSWER_COMMENTS_URL = API_URL + '/answers/%(ids)s/comments/?order=desc&sort=creation&site=stackoverflow'
    QUESTION_COMMENTS_URL = API_URL + '/questions/%(ids)s/comments/?order=desc&sort=creation&site=stackoverflow'
    QUESTIONS_URL = API_URL + '/questions?page=%(page)d&pagesize=100&fromdate=%(from)d&todate=%(to)d&order=desc&sort=activity&site=stackoverflow'
    TAG_SEPARATOR = ','
    VECTOR_DELIMITER = ';'
    XPATH_CONTENT = { 
			'question' : "//div[@id='question']//div[@class='post-text']",
			'answer'   : "//div[@id='answer-%([post_id)d']//div[@class='post-text']",
			'comment'  : "//div[@id='comment-%(post_id)d']//div[@class='comment-copy']"
		    }      
    Answers   = {}
    Questions = {}
    Comments  = {}
    
    def __init__(self):
      pass      
   
    def identify(self):
      return filter( lambda method: (not method[:1] == '_'), dir(self) )
    
    class dict_object(object):
      def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
	  setattr(self, k.replace('-', '_'), v)

    def __dict_to_object(self, d):
      return dict_object(**d) 
    
    def answer(self, _id):
      return self.Answers[_id]

    def fetch_questions(self, **kwargs):
      if not 'from' in kwargs:
	 ts_date_from = int(time()) - 2*86400 # results from approx 2 days ago
      else:
        ts_date_from = helper.datetime_to_timestamp(kwargs['from'])
      if not 'to' in kwargs:
	ts_date_to = int(time())
      else:
        ts_date_to   = helper.datetime_to_timestamp(kwargs['to'])
      if not 'page' in kwargs:
        kwargs['page'] = 1
      params = { 'page' : kwargs['page'], 'from' : ts_date_from, 'to' : ts_date_to }
      return self.__fetch_url(self.QUESTIONS_URL % params)

    def __fetch_comments(self, url_template, post_ids):
      if hasattr(post_ids, '__iter__'):
        ids = VECTOR_DELIMITER.join(post_ids)
      else:
	ids = str(post_ids)
      params = { 'ids' : ids }
      return self.__fetch_url(self.url_template % params)	  
    
    def fetch_answer_comments(self, post_id):
      return self.__fetch_comments(self.ANSWER_COMMENTS_URL, post_id)

    def fetch_question_comments(self, post_id):
      return self.__fetch_comments(self.QUESTION_COMMENTS_URL, post_id)

    def fetch_answers(self, question_id):
      if hasattr(question_id, '__iter__'):
	ids = VECTOR_DELIMITER.join(question_id)
      else:
	ids = str(question_id)
      params = { 'ids' : ids }	  
      return self.__fetch_url(self.ANSWERS_URL % params)
      

    def __fetch_url(self, url, compressed = True, json_format = True):
      request = Request(url)
      response = urlopen(request).read()
      if compressed:
	data = decompress(response, 16 + MAX_WBITS).decode('UTF-8')
      else:
	data = response.decode('UTF-8')
      if json_format:
	data = json.loads(data)  	
      return data      
       
    def fetch_text(self, url, post_type, post_id, delay = 0.01):
      page_html = self.__fetch_url(url, False, False)
      xpath = self.XPATH_CONTENT[post_type]%{ 'post_id' : post_id }
      page = parser.fromstring(page_html)
      element = page.xpath(xpath)
      time.sleep(delay)
      return u''.join(bsoup(htmltext(element[0])).findAll(text = True))

