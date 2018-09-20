# coding: utf-8
from xml.sax.saxutils import escape, quoteattr
from markupsafe import Markup
from qingmi.jinja import markup, markupper


def escape_list(*args):
    """ escape args in list
        return tuple type object
    """
    return tuple(escape(str(x)) for x in args)


def quoteattr_list(*args):
    """ quoteattr args in list
        return tuple type object
    """
    return tuple(quoteattr(str(x)) for x in args)


def text2short(text, max_lenth=20):
    """ long text to short text """
    if text is None:
        return ''
    text = str(text)
    return text[:max_lenth] + '...' if len(text) > max_lenth else text


def text2span(text, short_text, cls=''):
    """ text to span """
    if text.startswith('http://') or text.startswith('https://'):
        return '<a class=%s href=%s title=%s target="_blank">%s</a>' % (
            quoteattr_list(cls, text, text) + escape_list(short_text))
    return '<span class=%s title=%s>%s</span>' % (quoteattr_list(cls, text) + escape_list(short_text))


def text2link(text, link, max_lenth=20, blank=True, cls=''):
    """ text to link """
    tpl = '<a class=%s href=%s title=%s target="_blank">%s</a>'
    if not blank:
        tpl = '<a class=%s href=%s title=%s>%s</a>'
    text = text2short(text, max_lenth)
    if text or type(text) == int:
        return tpl % (quoteattr_list(cls, link, text) + (text,))
    return ''


def formatter(func):
    def wrapper(view, context, model, name):
        # `view` is current administrative view
        # `context` is instance of jinja2.runtime.Context
        # `model` is model instance
        # `name` is property name
        if hasattr(model.__class__, name):
            data = getattr(model, name)
            if data:
                return markup(func(data) or '')
        return ''
    return wrapper


def formatter_model(func):
    def wrapper(view, context, model, name):
        # `view` is current administrative view
        # `context` is instance of jinja2.runtime.Context
        # `model` is model instance
        # `name` is property name
        return markup(func(model) or '')
    return wrapper


def formatter_text(max_lenth=20, cls=''):
    @formatter
    def wrapper(data):
        data = str(data)
        if len(data) > max_lenth:
            return text2span(data, text2short(data, max_lenth), cls=cls)
        return data
    return wrapper


def formatter_link(func, max_lenth=20, blank=True, cls='', **kwargs):

    @formatter_model
    def wrapper(model):
        text, link = func(model)
        return text2link(text, link)

    return wrapper


@markupper
def bool_formatter(view, value, model, name, disabled=False, action='list'):
    url = view.get_url('.ajax_change')
    val = str(value)
    is_disable = 'disabled' if disabled else ''
    input_id = str(model.id) + '_' + name + '_' +  action

    html_tpl = """<div class="onoffswitch">
        <input type="checkbox" name="onoffswitch" class="onoffswitch-checkbox" id="%s" %s %s>
        <label class="onoffswitch-label" for="%s" data-id="%s" data-name="%s" data-value="%s" data-url="%s">
            <span class="onoffswitch-inner"></span>
            <span class="onoffswitch-switch"></span>
        </label>
    </div>""" % (input_id, 'checked' if value else '',
                is_disable,
                input_id, model.id, name, val, url)
    return html_tpl


@markupper
def select_formatter(view, value, model, name, choices):
    url = view.get_url('.ajax_change')
    selects = ''
    id = str(model.id)+str(name)

    for k, v in choices.items():
        select = '<li><a class="btn-formatter" data-key="%s" data-id="%s" data-name="%s" data-url="%s">%s</a></li>' % (k, model.id, name, url, v)
        selects = selects + select

    html = '''<div class="dropdown" style="min-width: 80px">
                <button id=%s class="btn btn-block btn-select" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" s>%s
                    <span class="caret"></span>
                </button>
                <ul class="dropdown-menu" aria-labelledby="dLabel" style="min-width:100px">%s</ul>
            </div>''' % (id, choices.get(str(value) if type(value) is Markup else value), selects)

    return html