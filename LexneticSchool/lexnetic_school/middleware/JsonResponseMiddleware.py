class JsonResponseMiddleware(object):
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		self.process_request(request)
		response = self.get_response(request)
		return response

	def process_request(self, request):
		if request.method in ("PUT", "PATCH") and request.content_type != "application/json":
			if hasattr(request, '_post'):
				del request._post
				del request._files
			try:
				initial_method = request.method
				request.method = "POST"
				request.META['REQUEST_METHOD'] = 'POST'
				request._load_post_and_files() # <----- this is the trick !!!!!!!!!!!!!!!!!
				request.META['REQUEST_METHOD'] = initial_method
				request.method = initial_method
			except Exception:
				pass
