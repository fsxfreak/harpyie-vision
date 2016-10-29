from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import math
import random

from django.http import JsonResponse

import globe_utils
from utils import *
from models import *

import json

# See classify/urls.py for why login_url is what it is
@login_required
def tag(request):
  return render(request, 'classify/tag.html')

@login_required
def tiles_retrieve(request):
  user_data = UserData.objects.get(user=request.user)
  # TODO Make the random distribution change
  random_index = random.randint(0, ImageConfig.objects.get(url='temp').tile_set.count() - 1)
  tile = ImageConfig.objects.get(url='temp').tile_set.all()[random_index]
  print(tile)
  user_data.tile = tile
  user_data.save()
  print(user_data.tile)

  # choose by user
  return JsonResponse({
      'lat1' : tile.lat1
    , 'lon1' : tile.lon1
    , 'lat2' : tile.lat2
    , 'lon2' : tile.lon2
    })

@login_required
def tag_spawn(request):
  if request.method == 'POST':
    y1 = request.POST.get('lat1', '')
    x1 = request.POST.get('lon1', '')
    y2 = request.POST.get('lat2', '')
    x2 = request.POST.get('lon2', '')

    success, lat1, lon1, lat2, lon2 = get_extents(y1, x1, y2, x2)
    if not success:
      return JsonResponse({ 'message' : 'failure' })
    user_data = UserData.objects.get(user=request.user)
    print(user_data)
    if user_data.tile is not None:
      ty1 = user_data.tile.lat1
      tx1 = user_data.tile.lon1
      ty2 = user_data.tile.lat2
      tx2 = user_data.tile.lon2
      if in_bounds(x1, y1, tx1, ty1, tx2, ty2) and in_bounds(x2, y2, tx1, ty1, tx2, ty2):
        # TODO Do something to handle how tags can be part of multiple tiles
        tag = Tag.objects.create(lat1 = lat1, lon1 = lon1, lat2 = lat2, lon2 = lon2, tile = user_data.tile)
    return JsonResponse({ 'message' : 'success' })
  return JsonResponse({ 'message', 'failure' })

@login_required
def images_configure(request):
  return render(request, 'classify/images-configure.html')

@login_required
def images_spawn(request):
  render_url = 'classify/images-configure.html'
  success = render(request, render_url, { 'message' : 'success' })
  failure = render(request, render_url, { 'message' : 'failure' })

  STEP_SIZE_METERS = 50

  if request.method == 'POST':
    img_name = request.POST.get('img_name', '')
    y1 = request.POST.get('lat1', '')
    x1 = request.POST.get('lon1', '')
    y2 = request.POST.get('lat2', '')
    x2 = request.POST.get('lon2', '')

    parsed, lat1, lon1, lat2, lon2 = get_extents(y1, x1, y2, x2)
    if not parsed:
      return failure

    globe = globe_utils.GlobalMercator()
    mx1, my1 = globe.LatLonToMeters(lat1, lon1)
    mx2, my2 = globe.LatLonToMeters(lat2, lon2)

    meters_x_step = abs(mx2 - mx1)
    meters_y_step = abs(my2 - my1)

    lon_step = (abs((lon2 - lon1)) / meters_x_step) * STEP_SIZE_METERS
    lat_step = (abs((lat2 - lat1)) / meters_y_step) * STEP_SIZE_METERS
    print ('%f, %f %f' % (mx1, my1, meters_x_step))
    print ('%f, %f %f' % (mx2, my2, meters_y_step))
    print ('lon_step: %f' % lon_step)
    print ('lat_step: %f' % lat_step)
    # TODO not hardcode image url
    image_config = ImageConfig.objects.get_or_create(url='temp')

    if image_config[1]:
      for x in xrange(0, int(math.ceil(meters_x_step / STEP_SIZE_METERS))):
        print ('row %i of %i' % (x, int(math.ceil(meters_x_step / STEP_SIZE_METERS))))
        for y in xrange(0, int(math.ceil(meters_y_step / STEP_SIZE_METERS))):
          # create a tile that has twice the size of the step size so that
          # there is significant overlap
          image_config[0].tile_set.create(lat1 = min(lat1, lat2) + y * lat_step,
                                          lon1 = min(lon1, lon2) + x * lon_step,
                                          lat2 = min(lat1, lat2) + (y + 2) * lat_step,
                                          lon2 = min(lon1, lon2) + (x + 2) * lon_step)

    return success
  else:
    return failure

