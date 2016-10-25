from django.shortcuts import render

from django.http import JsonResponse

def index(request):
  return render(request, 'classify/index.html')

def tag_spawn(request):
  if request.method == 'POST':
    return JsonResponse({ 'message' : 'success' })

  return JsonResponse({ 'message', 'failure' })

def images_configure(request):
	return render(request, 'classify/images-configure.html')

def images_spawn(request):
	render_url = 'classify/images-configure.html'
	success = render(request, render_url, { 'message' : 'success' })
	failure = render(request, render_url, { 'message' : 'failure' })

	if request.method == 'POST':
		img_name = request.POST.get('img_name', '')
		try:
			lat1 = float(request.POST.get('lat1', '0.0'))
			lon1 = float(request.POST.get('lon1', '0.0'))
			lat2 = float(request.POST.get('lat2', '0.0'))
			lon2 = float(request.POST.get('lon2', '0.0'))
		except ValueError: 	# non floats inputted
			return failure

		# TODO do something with the parameters (store in DB)
		print (lat1)
		return success
	else:
		return failure

