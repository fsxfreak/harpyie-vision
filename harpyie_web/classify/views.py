from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.http import JsonResponse

import globe_utils
from utils import *

import json

# See classify/urls.py for why login_url is what it is
@login_required
def tag(request):
  return render(request, 'classify/tag.html')

@login_required
def tiles_retrieve(request):
  username = request.user

  # choose by user
  return JsonResponse({
      'lat1' : 0.0
    , 'lon1' : 0.0
    , 'lat2' : 0.0
    , 'lon2' : 0.0
    })

@login_required
def tag_spawn(request):
  if request.method == 'POST':
    success, lat1, lon1, lat2, lon2 = get_extents(request.GET.get("lat1"), request.GET.get("lon1"), request.GET.get("lat2"), request.GET.get("lon2"))
    if not success:
      return JsonResponse({ 'message' : 'failure' })

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
    print ('%f, %f' % (mx1, my1))
    print ('%f, %f' % (mx2, my2))
    print ('lon_step: %f' % lon_step)
    print ('lat_step: %f' % lat_step)

    # TODO not hardcode image url
    image_config = ImageConfig.objects.create(url='temp')

    return success
  else:
    return failure

