from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save

from django.utils import timezone
import uuid
from uuid import UUID

class Tile(models.Model):
  # Tile.tag_set.all() is all the tags referencing this Tile

  def __unicode__(self):
    return 'TODO UNICODE TILE'

# UserData is created automagically along with each User object, used to store
# additional classify-specific data
class UserData(models.Model):
    user = models.OneToOneField(User)

    # UserData.tag_set.all() is all the tags referencing this User

    def __str__(self):
          return "%s's profile" % self.user

def create_user_profile(sender, instance, created, **kwargs):
    if created:
       profile, created = UserData.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)

class Tag(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

  lat1 = models.DecimalField(blank=False, editable=False, decimal_places=6, max_digits=10)
  lon1 = models.DecimalField(blank=False, editable=False, decimal_places=6, max_digits=10)
  lat2 = models.DecimalField(blank=False, editable=False, decimal_places=6, max_digits=10)
  lon2 = models.DecimalField(blank=False, editable=False, decimal_places=6, max_digits=10)

  tile = models.ForeignKey(Tile, on_delete=models.PROTECT)

  # TODO require a user later
  user = models.ForeignKey(UserData, on_delete=models.SET_NULL, blank=True, null=True)
  created = models.DateTimeField(editable=False, blank=True, null=True)

  def save(self, *args, **kwargs):
    if not self.created:
      self.created = timezone.now()
    return super(Tag, self).save(*args, **kwargs)

  def __unicode__(self):
    return 'TODO UNICODE TAG'

class ImageConfig(models.Model):
  # If an image is local, top level of url should be from 'static/'
  url = models.CharField(blank=False, max_length=255)

  def __unicode__(self):
    return 'TODO UNICODE IMAGECONFIG'