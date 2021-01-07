# coding: utf-8
from wtforms.widgets import html_params, HTMLString, TextArea
from markupsafe import Markup, escape
from qingmi.db.mongoengine.fields import FileProxy


__all__ = [
    'FileInput', 'ImageInput', 'AreaInput',
]


class FileInput(object):

    tmp = ('<div>'
           ' <input type="checkbox" name="%(marker)s">删除</input>'
           ' <i class="icon-file"></i>%(filename)s'
           '</div>')

    template = """
        %(placeholder)s
        <div class="input-group">
            <span class="input-group-btn">
                <div id="btn-choose" autocomplete="off" class="btn btn-default" style="width:80px;padding:0;">
                    <span style="padding: 6px 12px;display:inline-block;">选择文件</span>
                    %(input)s
                </div>
            </span>
            <input autocomplete="off" type="text" class="col-sm-5 form-control input-insert-image"
                placeholder='%(place)s' disabled="disabled" />
        </div>
        <div class="clearfix"></div>
    """

    def __call__(self, field, **kwargs):
        # if field.data and isinstance(field.data, FileProxy):
        #     data = field.data
        #     print('=======', data.content, type(data.content))
        #     print('=======', data.content.decode('utf-8'))

        kwargs.setdefault('id', field.id)
        kwargs.pop('class', None)
        kwargs.setdefault('autocomplete', 'off')
        kwargs.setdefault(
            'style',
            'width:100%;height:34px;margin-top:-34px;opacity:0;cursor:pointer;')
        kwargs.setdefault(
            'onchange',
            "$(this).parents('.input-group').find('.input-insert-image').val($(this).val())")

        placeholder = ''
        if field.data and isinstance(
                field.data,
                FileProxy) and field.data.filename:
            data = field.data

            placeholder = self.tmp % {
                'filename': escape(data.filename),
                # 'content_type': escape(data.content_type),
                # 'size': data.length // 1024,
                'marker': '%s-delete' % field.name
            }

        input = '<input %s>' % html_params(
            name=field.name, type='file', **kwargs)
        html = self.template % dict(
            placeholder=placeholder,
            place=field.place or field.label.text,
            input=input)
        return HTMLString(html)
        # kwargs.setdefault('id', field.id)

        # placeholder = ''
        # if field.data and isinstance(field.data, FileProxy):
        #     data = field.data

        #     placeholder = self.template % {
        #         'filename': escape(data.filename),
        #         # 'content_type': escape(data.content_type),
        #         # 'size': data.length // 1024,
        #         'marker': '_%s-delete' % field.name
        #     }

        # return HTMLString('%s<input %s>' % (placeholder,
        #                                     html_params(name=field.name,
        #                                                 type='file',
        #                                                 **kwargs)))


class ImageInput(object):

    template = """
        <a href="%(thumb)s" target="_blank">
            <div class="image-thumbnail">
                <img src="%(thumb)s">
            </div>
        </a>
        <div class="checkbox" style="margin-bottom:10px;">
            <label>
                <input name="%(name)s-delete" type="checkbox" value="true"> 删除 %(filename)s
            </label>
        </div>
    """

    input_tpl = """
        <div class="input-group">
            <span class="input-group-btn">
                <div id="btn-image" autocomplete="off" class="btn btn-default" style="width:80px;padding:0;">
                    <span style="padding: 6px 12px;display:inline-block;">选择图片</span>
                    %(input)s
                </div>
            </span>
            <input autocomplete="off" type="text" class="col-sm-5 form-control input-insert-image"
                placeholder='%(place)s' disabled="disabled" />
        </div>
        <div class="clearfix"></div>
    """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.pop('class', None)
        kwargs.setdefault('autocomplete', 'off')
        kwargs.setdefault(
            'style',
            'width:100%;height:34px;margin-top:-34px;opacity:0;cursor:pointer;')
        kwargs.setdefault(
            'onchange',
            "$(this).parents('.input-group').find('.input-insert-image').val($(this).val())")

        input = '<input %s>' % html_params(
            name=field.name, type='file', **kwargs)
        html = self.input_tpl % dict(
            place=field.place or field.label.text,
            input=input)
        if field.data and hasattr(field.data, 'link') and field.data.link:
            html = self.template % dict(
                thumb=field.data.link,
                name=field.name,
                filename=field.data.filename,
            ) + html

        return HTMLString(html)


class WangEditor(object):
    # class WangEditor(TextArea):

    template = """
    <textarea %s>\r\n%s</textarea>
    <div %s></div>
    """

    def __call__(self, field, **kwargs):
        # kwargs.setdefault('style', 'min-height:480px;resize:vertical;')
        script = """<script type="text/javascript">
            $(function() {
                var E = window.wangEditor;
                var editor = new E('#%s');
                var context_text = $('#%s');
                editor.customConfig.onchange = function (html) {
                    // 监控变化，同步更新到 textarea
                    var filterHtml = filterXSS(html);  // 此处进行 xss 攻击过滤
                    context_text.val(html)
                }
                editor.create();
                editor.txt.html(context_text.val());
                E.fullscreen.init('#%s');
                // 初始化 textarea 的值
                // context_text.val(editor.txt.html());

            });
        </script>""" % (field.name + 'editor', field.name, field.name + 'editor')

        html = self.template % (html_params(id=field.name, name=field.name,
                                            style='display: none;'),
                                field._value(),
                                html_params(id=field.name + 'editor'))

        # return Markup(html) + script
        return HTMLString(html) + script
        # return super(WangEditor, self).__call__(field, **kwargs) + script


class AreaInput(object):

    template = (
        '<div %s><div class="col-xs-4" style="padding: 0 8px 0 0;"><select %s></select></div>'
        '<div class="col-xs-4" style="padding: 0 8px"><select %s></select></div>'
        '<div class="col-xs-4" style="padding: 0 0 0 8px;"><select %s></select></div>'
        '<script type="text/javascript">area.init("%s", "%s", "%s", "%s")</script>'
        '<div class="clearfix"></div></div>')

    def __call__(self, field, **kwargs):
        datas = (field.data or '').split('|')
        if len(datas) == 3:
            province, city, county = datas
        else:
            province, city, county = '', '', ''
        province_name = '%s_province' % field.name
        city_name = '%s_city' % field.name
        county_name = '%s_county' % field.name
        return HTMLString(self.template % (
            html_params(id=field.name),
            html_params(id=province_name, name=province_name, **kwargs),
            html_params(id=city_name, name=city_name, **kwargs),
            html_params(id=county_name, name=county_name, **kwargs),
            field.name, province, city, county,
        ))
