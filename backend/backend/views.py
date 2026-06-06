from django.shortcuts import render


def spa_index_view(request):
    response = render(request, "index.html")
    response["Cache-Control"] = "no-cache, must-revalidate"
    response["Pragma"] = "no-cache"
    return response
