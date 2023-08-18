#import nessary files form django for view and url and to write restFul api using djangoRestFramework
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
# imprt httpstatus for status code
from http import HTTPStatus

import asyncio
import json
import re
from urllib.parse import urlparse, parse_qs, urlencode
import aiohttp

# import nessary files form worker for scrapping and other stuff
from worker.base import base
from worker.search import search
from worker.product import product


#remmber all the api are GET request and async view 

@api_view(["GET"])
async def baseView(request):
   
    response= await Response(base(request.get_host()), status=status.HTTP_200_OK)        
    return Response(status=HTTPStatus.OK, data=response.data)

@api_view(["Get"])
async def searchView(request):
    
    #extract the params form request django
    product=request.GET['product'] or 'latest fashion'
    host=request.get_host()
    try:
        response=await search(product,host)
        response=json.dumps(response)
        return Response(status=HTTPStatus.OK, data=response)
    except Exception as e:
        print(e)
        return Response(status=HTTPStatus.INTERNAL_SERVER_ERROR, data={"error": "internal server error from search view"})

@api_view(["Get"])
async def productView(request):

    url=request.get_full_path().split("/product/")[1]
    print(url)
    try:
        response=await product(url,"general")
        response=json.dumps(response)
        return Response(status=HTTPStatus.OK, data=response)
    except Exception as e:
        print(e)
        return Response(status=HTTPStatus.INTERNAL_SERVER_ERROR, data={"error": "internal server error form product view"})
