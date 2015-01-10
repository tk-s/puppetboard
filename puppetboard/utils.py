from __future__ import absolute_import
from __future__ import unicode_literals
from pprint import pprint

import json

from requests.exceptions import HTTPError, ConnectionError
from pypuppetdb.errors import EmptyResponseError

from flask import abort

def jsonprint(value):
  return json.dumps(value, indent=2, separators=(',', ': ') )


def get_or_abort(func, *args, **kwargs):
    """Execute the function with its arguments and handle the possible
    errors that might occur.

    In this case, if we get an exception we simply abort the request.
    """
    try:
        return func(*args, **kwargs)
    except HTTPError as e:
        abort(e.response.status_code)
    except ConnectionError:
        abort(500)
    except EmptyResponseError:
        abort(204)


def limit_reports(reports, limit):
    """Helper to yield a number of from the reports generator.

    This is an ugly solution at best...
    """
    for count, report in enumerate(reports):
        if count == limit:
            raise StopIteration
        yield report

def yield_or_stop(generator):
    """Similar in intent to get_or_abort this helper will iterate over our
    generators and handle certain errors.

    Since this is also used in streaming responses where we can't just abort
    a request we raise StopIteration.
    """
    while True:
        try:
            yield next(generator)
        except StopIteration:
            raise
        except (EmptyResponseError, ConnectionError, HTTPError):
            raise StopIteration

def eventcount_percentage(puppetdb, sum_by):
    events = puppetdb._query('aggregate-event-counts',
                             query='["=","latest-report?","true"]',
                             summarize_by=sum_by)
    pprint(events)
    events['failures_per'] = float(events['failures']) / float(events['total']) * 100
    events['skips_per'] = float(events['skips']) / float(events['total']) * 100
    events['successes_per'] = float(events['successes']) / float(events['total']) * 100
    events['noops_per'] = float(events['noops']) / float(events['total']) * 100
    return events

