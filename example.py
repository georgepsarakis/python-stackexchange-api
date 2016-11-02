#!/usr/bin/env python
from stackexchange import StackExchangeAPI, StackExchangeAPIRequest
from stackexchange.endpoints.answers import Answers

import warnings
warnings.filterwarnings("ignore")

if __name__ == "__main__":
    api = StackExchangeAPI()
    print api.version
    answers_endpoint = Answers()
    print answers_endpoint
    stack_overflow_request = StackExchangeAPIRequest().filter_by(
        'site',
        'stackoverflow'
    )
    comments_endpoint = answers_endpoint.filter(40314706).comments()
    print comments_endpoint
    so_request = api.request().filter_by('site', 'stackoverflow')
    response = so_request.using(comments_endpoint).fetch()
    print response

    for response in so_request.using(answers_endpoint):
        # print response.data['items']
        print response.request.parameters
        if response.request.parameters.get('page', 1) > 2:
            break

    for response in so_request.using(answers_endpoint)[1:4]:
        print response.request.parameters
        print response.data['items']

