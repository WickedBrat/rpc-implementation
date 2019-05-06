from copy import deepcopy


def unmarshal_boolean(arg):
    if int(arg) == 1:
        return True
    else:
        return False


def unmarshal_int(arg):
    return int(arg)


def unmarshal_float(arg):
    return float(arg)


def unmarshal_boolean_array(arg):
    for i, element in enumerate(arg):
        if type(element) == list:
            unmarshal_boolean_array(element)
        else:
            arg[i] = unmarshal_boolean(element)


def unmarshal(arg, arg_type):
    if arg_type == 'int':
        return unmarshal_int(arg)
    elif arg_type == 'boolean':
        return unmarshal_boolean(arg)
    elif arg_type == 'float':
        return unmarshal_float(arg)
    elif 'array' in arg_type and 'boolean' in arg_type:
        result = deepcopy(arg)
        unmarshal_boolean_array(result)

        return result

    return arg

