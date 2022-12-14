"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from ominer.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tweet', show, name='tweet'),
    path('collected', collect),
    path('queries', queries, name='queries'),
    path('queries/<int:pk>/', query_detail, name='query_detail'),
    path('queries/<int:pk>/datatable', datatable_detail, name='query_datatable'),
    path('queries/<int:pk>/gnetworktweet', gnetwork_detail_tweet, name='query_gnetwork'),
    path('queries/<int:pk>/gnetworkdomain', gnetwork_detail_domain, name='query_gnetwork_domain'),
    path('', include('users.urls')),

]