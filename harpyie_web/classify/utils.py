def get_extents(y1, x1, y2, x2):
  if not (y1 and x1 and y2 and x2):
    return False
  try:
    lat1 = float(y1)
    lon1 = float(x1)
    lat2 = float(y2)
    lon2 = float(x2)
  except ValueError:
    return False

  return True, lat1, lon1, lat2, lon2

def in_bounds(x1, y1, tx1, ty1, tx2, ty2):
  print("%f %f %f %f %f %f" % (x1, y1, tx1, ty1, tx2, ty2))
  return (x1 <= max(tx1, tx2)) and (x1 >= min(tx1, tx2)) and (y1 <= max(ty1, ty2)) and (y1 >= min(ty1, ty2))
