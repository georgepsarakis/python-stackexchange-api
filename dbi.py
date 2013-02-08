#!/usr/bin/python
import sys
import time, datetime
import MySQLdb as mysql
import lxml.html as parser
from lxml.etree import tostring as htmltext
import json, helper
from helper import *
from BeautifulSoup import BeautifulSoup as bsoup


class dbi:
    DBCursor = None
    Connection = None
    __defaults = { 'host'   : 'localhost',
                   'user'   : 'root',
		   'passwd' : '',
		   'db'     : ''
	         } 
    def __init__(self, **kwargs):
      try:
        for k, v in self.__defaults.iteritems():
          if not k in kwargs:
            kwargs[k] = v	    
        self.Connection = mysql.connect(host = kwargs['host'],
					user   = kwargs['user'],
		                        passwd = kwargs['passwd'],
		                        db     = kwargs['db'],
		                        use_unicode = True,
					charset = 'utf8'
                                        )
        self.DBCursor = self.Connection.cursor(mysql.cursors.DictCursor)
      except mysql.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
        	        
    def __quote_identifiers(self, s):
      return '`' + s.replace('`', '') + '`'

    def __interpolate(self, s):
      return '%(' + s + ')s'

    def __iterable_interpolate(self, l):
      return ', '.join(map(self.__interpolate, l))

    def __is_string(self, s):
      try:
        s += ''
      except:
        return False
      return True

    def truncate(self, table):
      try:
        self.DBCursor.execute('TRUNCATE ' + self.__quote_identifiers(table))
      except mysql.Error, e:
        self.__sql_error(e)
   
    def __build_insert_fields(self, table, params, ignore = True):
      if ignore:
        ignore = ' IGNORE '
      else:
	ignore = ' '	  
      return 'INSERT' + ignore + 'INTO '+ self.__quote_identifiers(table) + '(' + ', ' . join(map(self.__quote_identifiers, params.keys())) + ') VALUES'
    
    def __build_insert_values(self, params):
      return '(' + self.__iterable_interpolate(params.keys()) + ')'

    def insert(self, table, params, ignore = True):
      sql  = self.__build_insert_fields(table, params, ignore)     
      sql += self.__build_insert_values(params)
      for k, v in params.iteritems():
	if not self.__is_string(v):
	  v = unicode(v)  
	params[k] = v
      try:
        self.DBCursor.execute(sql, params)
      except mysql.Error, e:
        self.__sql_error(e)
        sys.exit(1)
      except mysql.Warning, ew:
        self.__sql_error(ew)	
      return self.DBCursor.lastrowid
   
    def __sql_error(self, e):
      print "Error %d: %s" % (e.args[0], e.args[1])
      print "Last SQL:", self.DBCursor._last_executed 
      self.Connection.rollback()
    
    def commit(self):
      self.Connection.commit()
    
    def __build_where(self, params, logical_and_functions = {}):
      fields = map(self.__quote_identifiers, params.keys())
      where = ' WHERE '
      last_field_index = len(params.keys()) - 1
      for seq, key in enumerate(params.keys()):
	 where_part = fields[seq]
	 has_operator = (key in logical_and_functions) and ('operator' in logical_and_functions[key])
	 if not has_operator:
	   where_part += '='
	 else:
	   where_part += logical_and_functions[key]['operator']
	 has_function =  (key in logical_and_functions) and ('function' in logical_and_functions[key])
	 if has_function:
	   where_part += logical_and_functions[key]['function'] + '('
         where_part += self.__interpolate(key)
	 if has_function:
           where_part += ')'  
         if seq < last_field_index:
	   if (key in logical_and_functions) and ('logical' in logical_and_functions[key]):
	     where_part += ' ' + logical_and_functions[key]['logical']
	   else:
	     where_part += ' AND '
	 where += where_part    
      return where
    
    def insert_if_not_exists(self, table, params, where_params, where_conditions = {}, return_field = 'id'):
      select_sql  = 'SELECT ' + self.__quote_identifiers(return_field) + ' FROM '
      select_sql += self.__quote_identifiers(table)
      select_sql += self.__build_where(where_params, where_conditions)
      r = self.select(select_sql, where_params, True, return_field)
      if r:
        return r
      else:
	return self.insert(table, params)  	

    def select(self, sql, params = {}, single_row = False, fetch_field_only = False):
      try:
        self.DBCursor.execute(sql, params)
	if single_row:
	  r = self.DBCursor.fetchone()
	else:  
          r = self.DBCursor.fetchall()
	if r and fetch_field_only:  
          return r[fetch_field_only]    	  
	return r
      except mysql.Error, e:
        self.__sql_error(e)


