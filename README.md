# Python Library for the StackExchange API

A Python library for easy access to the [StackExchangeAPI v2.1](http://api.stackexchange.com/).

The goal is to recreate the API methods as class methods so that someone just needs to familiarize with the API not the library itself to the possible extent.

Returned object (StackObject) properties can be accessed as dictionaries (`post["post_id"]`) or as object properties (`post.post_id`). You can also specify which fields to include in the result, if you do not need the entire object (this will consume less memory as well).

Every `"items"` array of the API response becomes an iterator using [itertools.imap](http://docs.python.org/2/library/itertools.html#itertools.imap).

Most API calls return an iterator which enables access to the next pages as long as you continue iterating.

## Methods

### set_param(param, value)

Set a global parameter (such as `pagesize`) to include in every request.

### set_auth(key=APP_KEY, token=ACCESS_TOKEN)

Apply these authentication credentials in every API call.

### ids(LIST_OF_IDS)

Sets the set of IDS for the next call. This is a convenience method and allows chaining (see the example.py sample code).

### posts

Returns a collection of posts.

### answers

Returns a collection of answers.

### questions

Returns a collection of questions.

### comments

Returns a collection of comments.
