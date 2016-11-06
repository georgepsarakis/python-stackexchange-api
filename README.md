# Python Wrapper for the StackExchange API

A Python library for easy access to the [StackExchange REST API v2](http://api.stackexchange.com/).

## Installation

Install with `pip`:

```
virtualenv env
source env/bin/activate
pip install .
# Verify
python -c 'import stackexchange'
```

## Usage

```python
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime, timedelta
import stackexchange
from stackexchange.api import StackExchangeAPI
from stackexchange.endpoints import Answers, Info

headers = {
    'User-Agent': 'Python-API-v{}'.format(stackexchange.__version__)
}

api = StackExchangeAPI(http_request_kwargs={'headers': headers})
stack_overflow_request = api.request().where(site='stackoverflow', pagesize=5)

now = datetime.utcnow()
stack_overflow_request = stack_overflow_request.where(
    from_date=now - timedelta(hours=2),
    to_date=now
)

answers_response = stack_overflow_request.using(Answers).fetch()
print answers_response

site_http_request = api.get_http_request(stack_overflow_request.using(Info))
print site_http_request.method, site_http_request.url, \
      site_http_request.headers, site_http_request.params

# Get the StackOverflow site information
stackoverflow_site_info = stack_overflow_request.using(Info).fetch()
print stackoverflow_site_info
print "StackOverflow Total Answers: {}".format(
    stackoverflow_site_info.items[0]['total_answers']
)

# Get the first 3 pages of answers
for response in stack_overflow_request.using(Answers).pagesize(1)[1:4]:
    print response
```
