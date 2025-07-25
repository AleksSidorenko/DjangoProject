# myapp/middleware.py

import logging
import time

logger = logging.getLogger('http_logger')

class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        logger.info(
            '%s %s %s %s %.2f sec',
            request.method,
            request.get_full_path(),
            response.status_code,
            request.META.get('REMOTE_ADDR'),
            duration
        )
        return response
