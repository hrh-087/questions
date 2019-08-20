from django.conf.urls import url, include
from django.views.generic import TemplateView
from . import views

# TemplateView => 基于类的视图 => 不用自己写视图函数

urlpatterns = [
    # url(r'register/$', TemplateView.as_view(template_name="accounts/register.html")),
    # url(r'register/$', views.register, name="register"),
    url(r'register/$', views.Register.as_view(), name="register"),
    # url(r'login/$',TemplateView.as_view(template_name="accounts/login.html"),name="login"),
    url(r'login/$',views.Login.as_view(),name="login"),
    url(r'logout/$',views.logout,name='logout'),
    # 忘记密码
    url(r'password/forget/$',views.PasswordForget.as_view(),name='password_forget'),
    # 重置密码
    url(r'password/reset/(\w+)$', views.PasswordReset.as_view(), name='password_reset')
]

