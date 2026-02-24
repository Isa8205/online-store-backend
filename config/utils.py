from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first to get the standard error response
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            'status': 'error',
            'message': 'Please correct the highlighted fields.',
            'fields': response.data
        }
        response.data = custom_data

    return response
