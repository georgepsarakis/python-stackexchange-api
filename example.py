#!/usr/bin/python
from StackAPI import StackAPI

if __name__ == "__main__":
  api = StackAPI()

  ''' Fetch site information '''
  info = api.info()
  info.total_answers
  info.total_comments
  
  ''' Fetch some posts '''
  for posts in api.posts():
    for post in posts:
      print post
    break
