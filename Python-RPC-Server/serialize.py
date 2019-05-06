from copy import deepcopy


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


def marshal(arg, arg_type):
    if arg_type == 'boolean':
        return marshal_boolean(arg)
    elif 'array' in arg_type and 'boolean' in arg_type:
        result = deepcopy(arg)
        marshal_boolean_array(result)

        return result

    return arg
