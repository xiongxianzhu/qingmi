from flask_mongoengine import Document
from qingmi.utils.encoding import smart_text


def get_model_field(model):
    """ get the verbose_name of all fields in the model """
    field_dict = dict()
    for field in model._fields:
        attr = getattr(model, field)
        if hasattr(attr, 'verbose_name'):
            verbose_name = attr.verbose_name
            if verbose_name:
                field_dict[field] = verbose_name
    return field_dict


def get_fields_in_model(instance):
    """
    Returns the list of fields in the given model instance. Checks whether to use the official _meta API or use the raw
    data. This method excludes many to many fields.
    :param instance: The model instance to get the fields for
    :type instance: Model
    :return: The list of fields for the given model (instance)
    :rtype: list
    """
    assert isinstance(instance, Document)
    return instance._fields


def model_instance_diff(old, new):
    """
    Calculates the differences between two model instances. One of the instances may be ``None`` (i.e., a newly
    created model or deleted model). This will cause all fields with a value to have changed (from ``None``).
    :param old: The old state of the model instance.
    :type old: Model
    :param new: The new state of the model instance.
    :type new: Model
    :return: A dictionary with the names of the changed fields as keys and a two tuple of the old and new field values
             as value.
    :rtype: dict
    """
    if not(old is None or isinstance(old, Document)):
        raise TypeError("The supplied old instance is not a valid model instance.")
    if not(new is None or isinstance(new, Document)):
        raise TypeError("The supplied new instance is not a valid model instance.")

    diff = {}

    if old is not None and new is not None:
        fields = set(list(old._fields.keys()) + list(new._fields.keys()))
    elif old is not None:
        fields = set(list(get_fields_in_model(old).keys()))
    elif new is not None:
        fields = set(list(get_fields_in_model(new).keys()))
    else:
        fields = set()

    for field in fields:
        try:
            old_value = smart_text(getattr(old, field, None))
        except Exception as e:
            old_value = None

        try:
            new_value = smart_text(getattr(new, field, None))
        except Exception as e:
            new_value = None

        if old_value != new_value:
            diff[field] = (smart_text(old_value), smart_text(new_value))

    if len(diff) == 0:
        diff = None

    return diff
