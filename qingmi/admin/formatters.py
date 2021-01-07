# coding: utf-8
from xml.sax.saxutils import escape, quoteattr
from markupsafe import Markup
from qingmi.jinja import markup, markupper
from qingmi.db.mongoengine.fields import FileProxy, ImageProxy


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


def text2short(text, max_length=20):
    """ long text to short text """
    if text is None:
        return ''
    text = str(text)
    return text[:max_length] + '...' if len(text) > max_length else text


def text2span(text, short_text, cls=''):
    """ text to span """
    if text.startswith('http://') or text.startswith('https://'):
        return '<a class=%s href=%s title=%s target="_blank">%s</a>' % (
            quoteattr_list(cls, text, text) + escape_list(short_text))
    return '<span class=%s title=%s>%s</span>' % (
        quoteattr_list(cls, text) + escape_list(short_text))


def text2link(text, link, max_length=20, blank=True, cls=''):
    """ text to link """
    tpl = '<a class=%s href=%s title=%s target="_blank">%s</a>'
    if not blank:
        tpl = '<a class=%s href=%s title=%s>%s</a>'
    text_short = text2short(text, max_length)
    if text or isinstance(text, int):
        return tpl % (quoteattr_list(cls, link, text) + (text_short,))
    return ''


def get_link(text, link, max_length=20, blank=True, html=False, **kwargs):
    if 'class_' in kwargs:
        kwargs['class'] = kwargs.pop('class_')
    attrs = dict()
    for k, v in kwargs.items():
        attrs[k.replace('_', '-')] = v

    tpl = '<a %shref=%s title=%s target="_blank">%s</a>'
    if not blank:
        tpl = '<a %shref=%s title=%s>%s</a>'
    if text or isinstance(text, int):
        extras = ' '.join('%s=%s' % (x, quoteattr(str(y)))
                          for x, y in attrs.items())
        extras = extras + ' ' if extras else ''
        if html:
            short = text
            text = ''
        else:
            short = str(text)[:max_length] + \
                '...' if len(str(text)) > max_length else str(text)
        return tpl % ((extras,) + quoteattr_list(link, text) +
                      (escape_list(short) if not html else (short,)))
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


def formatter_text(max_length=20, cls=''):
    @formatter
    def wrapper(data):
        data = str(data)
        if len(data) > max_length:
            return text2span(data, text2short(data, max_length), cls=cls)
        return data
    return wrapper


def formatter_link(func, max_length=20, blank=True, cls='', **kwargs):

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
    input_id = str(model.id) + '_' + name + '_' + action

    html_tpl = """<div class="onoffswitch">
        <input type="checkbox" name="onoffswitch" class="onoffswitch-checkbox" id="%s" %s %s>
        <label class="onoffswitch-label onoffswitch-action" for="%s" data-id="%s" data-name="%s" data-value="%s" data-url="%s">
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
    id = str(model.id) + str(name)

    for k, v in choices.items():
        select = '<li><a class="btn-formatter" data-key="%s" data-id="%s" data-name="%s" data-url="%s">%s</a></li>' % (
            k, model.id, name, url, v)
        selects = selects + select

    html = '''<div class="dropdown" style="min-width: 80px">
                <button id=%s class="btn btn-block btn-select" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" s>%s
                    <span class="caret"></span>
                </button>
                <ul class="dropdown-menu" aria-labelledby="dLabel" style="min-width:100px">%s</ul>
            </div>''' % (id, choices.get(str(value) if isinstance(value, Markup) else value), selects)

    return html


@markupper
def image_formatter(view, image):
    return format_image(image)


def format_image(image, link=True):
    if link:
        tpl = '''
            <a href=%s target="_blank" style="text-decoration:none">
                <img class="lazy" data-original=%s width=%s height=%s style="max-height: 40px;">
            </a>
        '''
        # tpl = '''
        #     <a href=%s target="_blank" style="text-decoration:none">
        #         <img class="lazy" data-original=%s width="40px" height="40px" style="max-height: 40px; margin: -6px 0">
        #     </a>
        # '''

        if image and image.link:
            # jquery lazyload懒加载图片得设置width, height, 否则不生效
            # 不改变图片比例， 缩放图片
            width, height = image.size
            h = 40
            w = width / (height / h)
            return tpl % quoteattr_list(
                image.link,
                image.link,
                str(w) + 'px',
                str(h) + 'px')
            # return tpl % quoteattr_list(image.link, image.link)
        return ''

    tpl = '''<img class="lazy" data-original=%s width=%s height=%s style="max-height: 40px;">'''
    if image and image.link:
        width, height = image.size
        h = 40
        w = width / (height / h)
        return tpl % quoteattr_list(image.link, str(w) + 'px', str(h) + 'px')
    return ''


@markupper
def file_formatter(view, file):
    return format_file(file)


def format_file(file, link=True):
    if link:
        tpl = '''
            <a href=%s target="_blank" style="text-decoration:none">
                <i class="fa fa-file" aria-hidden="true"></i>
            </a>
        '''
        if file and file.link:
            return tpl % quoteattr_list(file.link)
        return ''

    tpl = '''%s'''
    if file and file.filename:
        return tpl % quoteattr_list(proxy.filename)
    return ''


@markupper
def formatter_file(view, proxy):
    if isinstance(proxy, ImageProxy):
        return image_formatter(view, proxy)
    if isinstance(proxy, FileProxy):
        # return file_formatter(view, proxy)
        get_link(proxy.filename, proxy.link, max_length=40)
    return get_link(proxy.filename, proxy.link, max_length=60)


@markupper
def file_link_formatter(view, proxy):
    # return get_link(proxy.path, proxy.link, max_length=60)
    return get_link(proxy.filename, proxy.link, max_length=60)
