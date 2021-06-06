"""usermanagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

api_version = 'api/v1/'

urlpatterns = [
    path('o/', include('oauth2_provider.urls',
                       namespace='oauth2_provider')),
    path(api_version + 'accounts/', include('authentication.urls')),
    path(api_version + 'mfa/', include('mfa.urls')),
    path(api_version + 'notification/', include('notification.urls')),
    path(api_version + 'sms/', include("sms.urls")),
    path(api_version + 'fileupload/', include("fileupload.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    adminurl = [
        path('admin/', admin.site.urls),
    ]
    urlpatterns += adminurl
