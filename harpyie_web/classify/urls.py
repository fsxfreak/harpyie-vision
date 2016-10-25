from django.conf.urls import url
from . import views

urlpatterns = [
  url(r'^$', views.index, name='index'),

  # POST here to create an individual tag
  url(r'^tag/spawn/$', views.tag_spawn, name='tag/spawn'),

  # GET/POST here to configure image extents for tagging
  url(r'^images/configure/$', views.images_configure, name='images/configure'),
  url(r'^images/spawn/$', views.images_spawn, name='images/spawn')
]