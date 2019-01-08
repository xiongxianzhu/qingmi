from flask_mongoengine import Document


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
        fields = set(old._meta.fields + new._meta.fields)
        model_fields = actionslog.get_model_fields(new._meta.model)
    elif old is not None:
        fields = set(get_fields_in_model(old))
        model_fields = actionslog.get_model_fields(old._meta.model)
    elif new is not None:
        fields = set(get_fields_in_model(new))
        model_fields = actionslog.get_model_fields(new._meta.model)
    else:
        fields = set()
        model_fields = None
