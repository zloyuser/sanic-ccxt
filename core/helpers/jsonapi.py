def error(exception: Exception, title: str):
    return return_an_error({
        'title': title,
        'detail': str(exception)
    })


def return_an_error(*args):
    """List of errors

    Put all errors into a list of errors
    ref: http://jsonapi.org/format/#errors

    Args:
        *args: A tuple contain errors

    Returns:
        A dictionary contains a list of errors
    """
    list_errors = []
    list_errors.extend(list(args))

    return {
        'errors': list_errors
    }
