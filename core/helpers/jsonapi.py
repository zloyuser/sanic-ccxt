def error(exception: Exception, title: str):
    list_errors = []
    list_errors.extend(list({
        'title': title,
        'detail': str(exception)
    }))

    return {
        'errors': list_errors
    }
