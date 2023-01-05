from django.shortcuts import redirect

# Create your views here.
def redirect_docs(request):
	response = redirect('/api/docs')
	return response
