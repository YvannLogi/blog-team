from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def google_verification(request):
    return HttpResponse("google-site-verification: google0864d95fd0e70434.html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include("blog.urls", namespace="blog")),
    path("", include("core.urls", namespace="core")),

    path('google0864d95fd0e70434.html', google_verification),
]

if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    # En dev, Django sert lui-même les fichiers uploadés (/media/...)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Pages d'erreur personnalisées (actives seulement quand DEBUG=False)
handler400 = "core.views.bad_request"
handler403 = "core.views.permission_denied"
handler404 = "core.views.page_not_found"
handler500 = "core.views.server_error"
