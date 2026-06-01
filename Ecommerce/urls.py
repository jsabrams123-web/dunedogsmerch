from django.urls import path, include
# path: defines URL routes
# include: allows us to include app-level URLs


urlpatterns = [
    path('', include('store.urls')),
    # All main website URLs are handled by the store app
]
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
