"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import view

def chcek(request):
    
    if (request.method not in ['GET']):
        return {"error": "method not allowed", "status": 405}

urlpatterns = [
    path('search/', view.searchView, name='search'),
    path('product/', view.productView, name='product'),
    path('', view.baseView, name='base'),
    path('admin/', admin.site.urls),
]
