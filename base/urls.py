from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path("update_server/", views.update, name="update"),
    path('api/v1/', include('api.urls')),
]