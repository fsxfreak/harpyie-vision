from django.shortcuts import render

from django.http import JsonResponse

def index(request):
  return render(request, 'classify/index.html')

def tag_spawn(request):
  if request.method == 'POST':
    return JsonResponse({ 'message' : 'success' })

  return JsonResponse({ 'message', 'failure' })