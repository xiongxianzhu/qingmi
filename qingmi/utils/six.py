import functools
import itertools
import operator
import sys
import types


# Useful for very coarse version differentiation.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY34 = sys.version_info[0:2] >= (3, 4)

if PY3:
    string_types = str,
    integer_types = int,
    class_types = type,
    text_type = str
    binary_type = bytes

    MAXSIZE = sys.maxsize
else:
    string_types = basestring,
    integer_types = (int, long)
    class_types = (type, types.ClassType)
    text_type = unicode
    binary_type = str

    if sys.platform.startswith("java"):
        # Jython always uses 32 bits.
        MAXSIZE = int((1 << 31) - 1)
    else:
        # It's possible to have sizeof(long) != sizeof(Py_ssize_t).
        class X:

            def __len__(self):
                return 1 << 31
        try:
            len(X())
        except OverflowError:
            # 32-bit
            MAXSIZE = int((1 << 31) - 1)
        else:
            # 64-bit
            MAXSIZE = int((1 << 63) - 1)
        del X

if PY3:
    def iterkeys(d, **kw):
        return iter(d.keys(**kw))

    def itervalues(d, **kw):
        return iter(d.values(**kw))

    def iteritems(d, **kw):
        return iter(d.items(**kw))

    def iterlists(d, **kw):
        return iter(d.lists(**kw))

    viewkeys = operator.methodcaller("keys")

    viewvalues = operator.methodcaller("values")

    viewitems = operator.methodcaller("items")
else:
    def iterkeys(d, **kw):
        return d.iterkeys(**kw)

    def itervalues(d, **kw):
        return d.itervalues(**kw)

    def iteritems(d, **kw):
        return d.iteritems(**kw)

    def iterlists(d, **kw):
        return d.iterlists(**kw)

    viewkeys = operator.methodcaller("viewkeys")

    viewvalues = operator.methodcaller("viewvalues")

    viewitems = operator.methodcaller("viewitems")
