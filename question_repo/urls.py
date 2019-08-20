"""question_repo URL Configuration

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
from apps.repo import views
from django.views.static import serve
from  .settings import MEDIA_ROOT
from django.views.generic import TemplateView
from django.conf.urls import  handler404,handler500

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'^login/$', views.login, name="login"),

    # url(r'^register/$', views.register),
    # url(r'^index/$', views.index, name='index'),
    # url(r'^questions/$', views.questions),
    # accounts
    url(r'base/$',TemplateView.as_view(template_name='uc_base.html')),
    url(r'^accounts/', include('apps.accounts.urls', namespace='accounts')),
    url(r'^apis/', include('apps.apis.urls', namespace='apis')),
    url(r'^uc/', include('apps.usercenter.urls', namespace='uc')),
    # repo
    url(r'^', include('apps.repo.urls', namespace='repo')),
    # meida 处理
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    # ckeditor
    # url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    # url(r'^uc/',include('apps.usercenter.urls',namespace='uc'))
    # url(r'^captcha/', include('captcha.urls')),
]
handler404 = views.custom_404

handler500 = views.custom_500