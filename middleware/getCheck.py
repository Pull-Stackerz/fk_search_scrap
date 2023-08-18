from typing import Any
from rest_framework.response import Response
from rest_framework import status
import json


# not mounted yet
class sanityCheck:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method != "GET":
            response = Response(
                data={"error": "Method not allowed", "status": 405},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
            return response

        response = self.get_response(request)
        return response
