# 12_GBPAPP/config/urls.py

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Páginas principais (home, login, inserção, cálculo)
    path('',       include('apps.pages.urls')),

    # Outras apps que você tinha
    path('',       include('apps.dyn_dt.urls')),
    path('',       include('apps.dyn_api.urls')),
    path('charts/',include('apps.charts.urls')),

    # Admin Soft, se for necessário
    path('',       include('admin_soft.urls')),
]
