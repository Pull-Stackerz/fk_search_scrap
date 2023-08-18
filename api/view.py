# import nessary files form django for view and url and to write restFul api using djangoRestFramework
from django.urls import path

# from rest_framework.decorators import api_view
from adrf.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

# imprt httpstatus for status code
from http import HTTPStatus
import json
import re
from urllib.parse import urlparse, parse_qs, urlencode
import aiohttp
import asyncio

# import nessary files form worker for scrapping and other stuff
from worker.base import base
from worker.search import search
from worker.product import product


# remmber all the api are GET request and async view


@api_view(["GET"])
def baseView(request):
    print("base view called", "\n\n\n")
    response = base(request.get_host())
    return Response(status=HTTPStatus.OK, data=response)


@api_view(["Get"])
async def searchView(request):
    # extract the params form request django
    product = request.GET["product"] or "latest fashion"
    host = request.get_host()
    try:
        # print("\n\n\n", request.headers.get("Authorization"), "\n\n\n")
        response = await search(product, host)
        print(response)
        # response = json.dumps(response)
        return Response(status=HTTPStatus.OK, data=response)
    except Exception as e:
        print(e)
        return Response(
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            data={"error": "internal server error from search view"},
        )


@api_view(["GET"])
def test(request, product_identifier):
    print("\n\n\n", product_identifier, "\n\n\n")
    return Response({"message": f"Product Identifier: {product_identifier}"})


@api_view(["Get"])
async def productView(request):
    # print("\n\n\nentere\n\n\n")

    # print(url)
    # return Response(status=HTTPStatus.OK, data={})
    try:
        url = request.GET["query"][1:]
        # print(url, "\n\n\n")
        # return Response(status=HTTPStatus.OK, data={})
        # return Response(status=HTTPStatus.OK, data={})
        response = await product(url, "general")
        # response = json.dumps(response)
        return Response(status=HTTPStatus.OK, data=response)
    except Exception as e:
        print(e)
        return Response(
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            data={"error": "internal server error form product view"},
        )
