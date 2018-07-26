def error(exception: Exception, title: str):
    return {
        'errors': [
            {
                'title': title,
                'detail': str(exception)
            }
        ]
    }
