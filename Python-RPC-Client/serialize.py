import copy


def marshal_boolean(arg):
    if arg:
        return '1'
    else:
        return '0'


def marshal_boolean_array(arg):
    for i, element in enumerate(arg):
        if type(element) == list:
            marshal_boolean_array(element)
        else:
            arg[i] = marshal_boolean(element)


def marshal(arg, type):
    if type == 'boolean':
        return marshal_boolean(arg)
    elif 'array' in type and 'boolean' in type:
        result = copy.deepcopy(arg)
        marshal_boolean_array(result)

        return result

    return arg
