#!/usr/bin/python
from StackAPI import StackAPI

if __name__ == "__main__":
  api = StackAPI()

  ''' Fetch site information '''
  info = api.info()
  print info.total_answers
  print info.total_comments
  
  ''' Fetch some posts '''
  api.set_param('pagesize', 4)  
  try:
    for posts in api.posts(fields=['post_id', 'creation_date', 'link', 'score', 'post_type' ]):
      for post in posts:
        print post
      break
  except:
    print api.last_error()
  print 'URL >> ', api.LAST_URL
  
  posts = api.ids([20904085, 20904422]).order('votes').posts()
  for page in posts:
    for post in page:
      print post
    break
  print 'URL >> ', api.LAST_URL
  print "ERROR: ", api.last_error()
