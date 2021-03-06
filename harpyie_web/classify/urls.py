from django.conf.urls import url

from django.contrib import auth
import django.contrib.auth.views
from . import views

urlpatterns = [
  url(r'^$', views.tag, name='tag'),

  url(r'^accounts/login/$', views.loginuser, name='login'),

  url(r'^accounts/create/$', views.adduser, name='create'),

  url(r'^accounts/logout/$', auth.views.logout,
      { 'next_page': '/e4e/ml_training_map/harpy_web/accounts/login' }, name='logout'),

  # GET here to retrieve extents for an individual tile
  url(r'^tiles/retrieve/$', views.tiles_retrieve, name='tiles/retrieve'),

  # POST here to create an individual tag
  url(r'^tag/spawn/$', views.tag_spawn, name='tag/spawn'),

  # GET/POST here to configure image extents for tagging
  url(r'^images/configure/$', views.images_configure, name='images/configure'),

  url(r'^images/spawn/$', views.images_spawn, name='images/spawn'),

  # GET here to download the csv
  url(r'^tags/download/$', views.tags_download, name='tags/download'),

  url(r'^tiles/download/$', views.tiles_download, name='tiles/download'),
]
