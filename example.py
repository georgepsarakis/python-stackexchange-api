#!/usr/bin/python
from StackAPI import StackAPI

if __name__ == "__main__":
  api = StackAPI()

  ''' Fetch site information '''
  info = api.info()
  print info.total_answers
  print info.total_comments
  api.set_param('pagesize', 4)  
  ''' Fetch some posts '''
  try:
    for posts in api.posts(fields=['post_id', 'creation_date', 'link', 'score', 'post_type' ]):
      for post in posts:
        print post
      break
  except:
    print api.last_error()
