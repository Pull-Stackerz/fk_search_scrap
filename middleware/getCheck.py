from typing import Any
from rest_framework.response import Response
from rest_framework import status
import json

# not mounted yet 
class sanityCheck:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request) -> Any:
        if request.method not in ["GET"]:
            return Response(
                data={"error": "method not allowed", "status": 405},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        return self.get_response(request)
