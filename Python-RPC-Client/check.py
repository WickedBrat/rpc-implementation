def check_array(arg, type):
    array_type = type[6: len(type) - 1]

    for element in arg:
        if not check_arg(element, array_type):
            return False

    return True


def check_arg(arg, type):
    if type == 'int':
        return isinstance(arg, int)
    elif type == 'string':
        return isinstance(arg, str)
    elif type == 'char':
        return isinstance(arg, str) and len(arg) == 1
    elif type == 'float':
        return isinstance(arg, float)
    elif type == 'boolean':
        return isinstance(arg, bool)
    elif type[:5] == 'array':
        return check_array(arg, type)
