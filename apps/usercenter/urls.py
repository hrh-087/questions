from django.conf.urls import url, include
from . import views

urlpatterns = [
    # 个人资料
    url(r'^profile/$',views.ProfileView.as_view(),name='profile'),
    #　修改密码
    url(r'^change_passwd/$',views.ChangePasswdView.as_view(),name='change_passwd'),
    # 我的回答
    url(r'answer/$',views.AnswerView.as_view(),name="answer"),
    # 我的收藏
    url(r'collect/$',views.CollectView.as_view(),name='collect'),
    # 我的贡献
    url(r'contribut/$', views.ContributeView.as_view(), name='contribut'),

    # 我的权限
    url(r"^approval/$",views.ApprovalView.as_view(),name="approval"),
    # 审核接口

    url(r'^approval/(?P<id>\d+)/$', views.ApprovalPassView.as_view(), name='approval_pass'),
]




