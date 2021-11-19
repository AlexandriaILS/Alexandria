from django.shortcuts import render

def bad_request(request, exception):
    return render(request, "400.html", {'error': exception}, status=400)


def permission_denied(request, exception):
    return render(request, "403.html", {'error': exception}, status=403)


def not_found(request, exception):
    return render(request, "404.html", {'error': exception}, status=404)


def server_error(request):
    return render(request, "500.html", status=500)
