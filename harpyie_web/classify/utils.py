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