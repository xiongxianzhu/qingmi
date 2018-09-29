# coding: utf-8
from wtforms.widgets import html_params, HTMLString, TextArea
from markupsafe import Markup, escape


__all__ = [
    'FileInput', 'ImageInput',
]


class FileInput(object):

    template = """
        <div class="input-group">
            <span class="input-group-btn">
                <div id="btn-image" autocomplete="off" class="btn btn-default" style="width:80px;padding:0;">
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
        kwargs.setdefault('id', field.id)
        kwargs.pop('class', None)
        kwargs.setdefault('autocomplete', 'off')
        kwargs.setdefault('style', 'width:100%;height:34px;margin-top:-34px;opacity:0;cursor:pointer;')
        kwargs.setdefault('onchange', "$(this).parents('.input-group').find('.input-insert-image').val($(this).val())")
        input = '<input %s>' % html_params(name=field.name, type='file', **kwargs)
        html = self.template % dict(place=field.place or field.label.text, input=input)
        return HTMLString(html)


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
        kwargs.setdefault('style', 'width:100%;height:34px;margin-top:-34px;opacity:0;cursor:pointer;')
        kwargs.setdefault('onchange', "$(this).parents('.input-group').find('.input-insert-image').val($(this).val())")

        input = '<input %s>' % html_params(name=field.name, type='file', **kwargs)
        html = self.input_tpl % dict(place=field.place or field.label.text, input=input)
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
        kwargs.setdefault('style', 'height:480px;')
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
                // 初始化 textarea 的值
                // context_text.val(editor.txt.html());
                
            });
        </script>""" % (field.name+'editor', field.name)

        html = self.template % (html_params(id=field.name, name=field.name,
            style='display: none;'),
            field._value(),
            html_params(id=field.name+'editor'))

        # return Markup(html) + script
        return HTMLString(html) + script
        # return super(WangEditor, self).__call__(field, **kwargs) + script