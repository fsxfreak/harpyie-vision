from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from django.db.models import Count
from django.db.models import Min

import math
import random
from PIL import Image
import os
from forms import *

from django.http import HttpResponseRedirect

import globe_utils
from utils import *
from models import *

import csv
import json

def loginuser(request):
  form = LoginForm()
  if request.method == 'POST':
    form = LoginForm(request.POST)
    if form.is_valid():
      login(request, User.objects.get(username=form.cleaned_data['username']))
      return HttpResponseRedirect('/e4e/ml_training_map/harpy_web/')
  variables = {
      'form': form
  }
  return render(request, 'classify/login.html', variables)



  
# See classify/urls.py for why login_url is what it is
@login_required
def tag(request):
  return render(request, 'classify/tag.html')

@login_required
def tiles_retrieve(request):
  user_data = UserData.objects.get(user=request.user)
  # check if the user's previous tile is complete
  complete = request.GET.get('complete', '')
  if complete == 'yes':
    # add current tile to list of completed tiles
    user_data.tiles.add(user_data.tile)
    # for every user that complete the tile, halve its weight
    #NOTE Since individual weights are not kept track of (things just subtract from total weight),
    #     if the user list is manually set, the weight values may break.
    #     Additionally, this code assumes each Tile starts with weight 1
    #     It might end up being not worth it to keep track of weights,
    #     and just recalculating the total weights on each request may be easier/fast enough
    #     I don't know much about databases so this might not be the best way
    #TODO Make it so you can manually set user list/tile weight
    #     and make a function to update total weight values
    user_data.tile.image_config.total_weight -= 1 / float(2**user_data.tile.viewed_users.count())
    user_data.tile.image_config.save()
    uiw = request.user.userimageweight_set.get(image=user_data.tile.image_config)
    # since the weight of this tile should be 0 for this user, it should be reduced
    # by twice as much as the other tiles
    uiw.weight -= 2 / float(2**user_data.tile.viewed_users.count())
    uiw.save()
    # halve the tile's weight for each of the other users
    for ud in UserData.objects.all():
      if not ud in user_data.tile.viewed_users.all():
        uiw = ud.user.userimageweight_set.get(image=user_data.tile.image_config)
        uiw.weight -= 1 / float(2**user_data.tile.viewed_users.count())
        uiw.save()


  # TODO Use the weights above to change the odds of tiles being chosen
  #      Currently, since weights are not used, tiles that should have 0
  #      probability have a (low) chance of being chosen, which could result in
  #      negative weights (which doesn't matter yet since weights aren't used
  labeled_tiles = ImageConfig.objects.all()[0].tile_set.filter(use = True).exclude(viewed_users__in=[user_data]).annotate(num_users=Count('viewed_users'))
  min_users = labeled_tiles.aggregate(Min('num_users'))['num_users__min']
  valid_tiles = labeled_tiles.filter(num_users=min_users)
  random_index = random.randint(0, valid_tiles.count())
  tile = valid_tiles[random_index]
  #random_index = random.randint(0, ImageConfig.objects.all()[0].tile_set.count() - 1)
  #tile = ImageConfig.objects.all()[0].tile_set.all()[random_index]
  user_data.tile = tile
  user_data.save()

  # choose by user
  return JsonResponse({
      'lat1' : tile.lat1
    , 'lon1' : tile.lon1
    , 'lat2' : tile.lat2
    , 'lon2' : tile.lon2
    , 'tiles' : user_data.tiles.count()
    , 'tags' : user_data.tag_set.count()
    , 'img_name' : tile.image_config.url
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
    if user_data.tile is not None:
      fty1 = user_data.tile.lat1
      ftx1 = user_data.tile.lon1
      fty2 = user_data.tile.lat2
      ftx2 = user_data.tile.lon2
      works, tx1, tx2, ty1, ty2 = get_extents(ftx1, ftx2, fty1, fty2)
      # sometimes the view is slightly bigger than the actual tile that is served,
      # but this just cuts out selections that are not in the tile
      if in_bounds(lon1, lat1, tx1, ty1, tx2, ty2) or in_bounds(lon2, lat2, tx1, ty1, tx2, ty2) or in_bounds(lon1, lat2, tx1, ty1, tx2, ty2) or in_bounds(lon2, lat1, tx1, ty1, tx2, ty2):
        # TODO Do something to handle how tags can be part of multiple tiles
        tag = Tag.objects.create(lat1 = lat1, lon1 = lon1, lat2 = lat2, lon2 = lon2, tile = user_data.tile, user = user_data)
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
    image_config = ImageConfig.objects.get_or_create(url=request.POST.get('img_name', ''), total_weight=0)

    print(os.listdir('classify/static/imgs/'))
    if image_config[1]:
      img = 0
      alpha = 0
      tile_pos = (-1, -1)
      total = 0

      # get the lowest resolution image of the map so that it can be used to
      # calculate how empty tiles are
      min_zoom = int(sorted(os.listdir('classify/static/imgs/'))[0])
      for x in xrange(0, int(math.ceil(meters_x_step / STEP_SIZE_METERS))):
        print ('row %i of %i' % (x, int(math.ceil(meters_x_step / STEP_SIZE_METERS))))
        for y in xrange(0, int(math.ceil(meters_y_step / STEP_SIZE_METERS))):
          left = min(lat1, lat2) + y * lat_step
          top = min(lon1, lon2) + x * lon_step
          right = min(lat1, lat2) + (y + 2) * lat_step
          bottom = min(lon1, lon2) + (x + 2) * lon_step
          px1, py1 = globe.MetersToPixels(*(globe.LatLonToMeters(left, top)+(min_zoom,)))
          px2, py2 = globe.MetersToPixels(*(globe.LatLonToMeters(right, bottom)+(min_zoom,)))
          area = (int(round(px2)) - int(round(px1))) * (int(round(py2)) - int(round(py1)))
          fill = 0;
          image_size = 256
          empty = False
          # TODO Optimize this (do something like getting the total of each quarter
          #      of a tile, then sum the right ones up & either preload all images or
          #      move through the map in a way that reloads images less)
          # Keeps track of what fraction of a tile has information
          # can either use this to make less filled tiles less likely to be shown,
          # or can just not include the tiles if they are too empty
          for px in xrange(int(round(px1)), int(round(px2))):
            for py in xrange(int(round(py1)), int(round(py2))):
              if not globe.PixelsToTile(px, py) == tile_pos:
                tile_pos = globe.PixelsToTile(px, py)
                img = Image.open('classify/static/imgs/%i/%i/%i.png' % (min_zoom, tile_pos[0], tile_pos[1]), 'r')
                alpha = img.split()[-1].getdata()
              # the tiles y value increases going up, but the pixel values in the images increase going down
              # so you have to subtract the y coordinate from 1 less than the image size
              if alpha[(px % image_size) + image_size * ((image_size-1) - (py % image_size))] == 0:
                  empty = True
              fill += alpha[(px % image_size) + image_size * ((image_size-1) - (py % image_size))]
          # only add a tile if it is at least 80% full
          if fill / float(area*255) > 0.8:
            # create a tile that has twice the size of the step size so that
            # there is significant overlap
            image_config[0].tile_set.create(lat1 = left,
                                            lon1 = top,
                                            lat2 = right,
                                            lon2 = bottom,
                                            fill = fill / float(area*255))
            total += 1
      image_config[0].total_weight = total
      image_config[0].save()
      for user in User.objects.all():
        user.userimageweight_set.create(image = image_config[0],
                                       weight = total)

    return success
  else:
    return failure

def setuse():
    for tile in Tile.objects.all():
        width = abs(tile.lat2 - tile.lat1)
        height = abs(tile.lon2 - tile.lon1)
        tile.use = (abs(tile.lat1) % width > width/2) and (abs(tile.lon1) % height > height/2)
        tile.save()

def adduser(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(form.cleaned_data['username'])
            for img in ImageConfig.objects.all():
                img.userimageweight_set.create(user = new_user,
                                               weight = img.total_weight)
            return HttpResponseRedirect('/e4e/ml_training_map/harpy_web/')
    else:
        form = UserForm()

    return render(request, 'classify/adduser.html', {'form': form})

@login_required
def tags_download(request):
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="tags.csv"'

  writer = csv.writer(response)
  writer.writerow(['lat1', 'lon1', 'lat2', 'lon2', 'user', 'timestamp', 'uuid'])
  tags = Tag.objects.all()
  for tag in tags:
    writer.writerow([tag.lat1, tag.lon2, tag.lat2, tag.lon1, tag.user.user.username, tag.created, tag.id])

  return response

@login_required
def tiles_download(request):
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="tiles.csv"'
  labeled_tiles = ImageConfig.objects.all()[0].tile_set.filter(use = True).annotate(num_users=Count('viewed_users'))
  writer = csv.writer(response)
  writer.writerow(['tileid','tilelat1','tilelon1','tilelat2','tilelon2','lat1', 'lon1', 'lat2', 'lon2', 'user', 'timestamp', 'uuid'])
  for tile in labeled_tiles.filter(num_users__gt=0):
    for tag in tile.tag_set.all():
      writer.writerow([tile.id, tile.lat2, tile.lon1, tile.lat1, tile.lon2, tag.lat1, tag.lon2, tag.lat2, tag.lon1, tag.user.user.username, tag.created, tag.id])
  return response
