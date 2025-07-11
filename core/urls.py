from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('authentication.api.urls')),
    path('api/', include('market.api.urls')),
    path('api/', include('users.api.urls')),   
]

