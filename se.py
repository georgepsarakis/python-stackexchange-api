#!/usr/bin/python
import sys, binascii
import helper
import dbi, stackAPI

dbi = dbi.dbi(db = 'so_testing')

tables = ['questions_tags', 'comments', 'answers', 'tags', 'questions', 'users']

for table in tables:
  print 'Truncating %s'%(table,)
  dbi.truncate(table)

stackapi = stackAPI.stackAPI()

question_field_map = {
    'creation_date'  : { 'db_field' : 'date_created', 'type' : 'date'   },
    'question_id'    : { 'db_field' : 'so_id',        'type' : 'int'    },
    'link'           : { 'db_field' : 'link',         'type' : 'string' },
    'view_count'     : { 'db_field' : 'view_count',   'type' : 'int'    },
    'title'          : { 'db_field' : 'title',        'type' : 'string' },
    'owner->user_id' : { 'db_field' : 'user_id',      'type' : 'int'     }
}

user_field_map = {
  #'creation_date' : { 'db_field' : 'date_created', 'type' : 'date'  },
  'user_id'       : { 'db_field' : 'so_id',        'type' : 'int'    },
  'display_name'  : { 'db_field' : 'display_name', 'type' : 'string' },
  'reputation'    : { 'db_field' : 'reputation',   'type' : 'int'    },
  'link'          : { 'db_field' : 'link',         'type' : 'string' }
}

date_function_map = {
  'int'    : int,
  'date'   : helper.timestamp_to_datetime,
  'string' : unicode 
}

def insert_user(post_data):
  global dbi, user_field_map
  user = post_data['owner']
  fk_params = {}
  for fk_k, fk_v in user_field_map.iteritems():
    fk_param_value = user[fk_k]
    if 'type' in date_function_map:
      fk_param_value = date_function_map[fk_v['type']](fk_param_value)
    fk_params[fk_v['db_field']] = fk_param_value
  dbi.insert('users', fk_params, True) 
  dbi.commit()


for page in range(1, 3):
  user_ids = []
  print 'Page:', page
  questions = stackapi.fetch_questions(page = page)
  question_ids = []
  for q in questions['items']:      
      params = {}
      for k, v in question_field_map.iteritems():
	if k.find('->') > -1:
	  keys = k.split('->')
	  param_value = q
	  for key in keys:
	    param_value = param_value[key]   
	  if keys[0] == 'owner':
            insert_user(q)   
	else:  
          param_value = q[k]
	if v['type'] == 'date':
          param_value = helper.timestamp_to_datetime(int(param_value))
	elif v['type'] == 'int':
	  param_value = int(param_value)  
	elif v['type'] == 'string':
	  pass  
        params[v['db_field']] = param_value
      params['content'] = stackapi.fetch_text( q['link'], 'question', q['question_id'])
      question_id = dbi.insert('questions', params)
      tag_ids = []
      for tag in q['tags']:
	tag_params = { 'name' : tag, 'tag_key' : binascii.crc32(tag) & 0xffffffff }  
        tag_id = dbi.insert_if_not_exists('tags', tag_params, tag_params)
	dbi.insert('questions_tags', { 'question_id' : question_id, 'tag_id' : tag_id })
      dbi.commit()
      questions_ids.append(q['question_id'])
  question_comments = stackapi.fetch_question_comments(question_ids)
  answers = stackapi.fetch_answers(question_ids)
  answer_comments = stackapi.fetch_answer_comments( [ answer['answer_id'] for answer in answers['items'] ] )

'''
---------------------- NOTES --------------------
'''

'''
import lxml.html as H
doc  = H.fromstring(html)
node = doc.xpath("//div[@class='mydiv']")
http://stackoverflow.com/questions/6198107/python-html-parsing
'''

''' Parse answer text:
<div id="answer-8484994" class="answer" data-answerid="8484994" style="">
class="answercell" -> class="post-text"
'''

''' Parse question text:
<div class="question" id="question" data-questionid="8484264">
 -> class="post-text"
'''

''' Parse comment text:
 <tr id="comment-5961420" class="comment">
 <span class="comment-copy">What is the content of try1.cpp?</span>
'''

