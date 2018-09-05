# coding: utf-8

from urlparse import urlparse, urljoin
from flask import request, url_for


def is_safe_url(target):
    """
    A function that ensures that a redirect target will 
    lead to the same server is here
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    """ looks at various hints to find the redirect target """
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

def redirect_back(endpoint, **values):
    """ 
    make sure that the actual back redirect is slightly different
    (only use the submitted data, not the referrer)
    """
    target = request.form['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)
