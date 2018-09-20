"""backtest_py2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve
from rest_framework.routers import DefaultRouter
from backtest_py2.settings import MEDIA_ROOT
from users.views import UserViewset, UserLogin, change_password
from report.views import ReportsViewSet, upload_report
from file.views import download_key
import xadmin

router = DefaultRouter()
router.register(r'api/report', ReportsViewSet, base_name="reports")
router.register(r'api/users', UserViewset, base_name="users")

urlpatterns = [
    url(r'^api/xadmin/', xadmin.site.urls),
    url(r'api/media/<path:path>', serve, {'document_root':MEDIA_ROOT}),
    url(r'api/image/<path:path>', serve, {'document_root':MEDIA_ROOT}),
    url(r'^api/files/(?P<report>.*)/(?P<file_name>.*)?/?$', download_key, name='download-file'),
    url(r'api/login/', UserLogin.as_view(), name='login'),
    url(r'api/users/change_password/', change_password, name='change-password'),
    url(r'api/upload/', upload_report, name='upload-report'),
    url(r'', include(router.urls))
]
