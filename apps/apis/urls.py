from django.conf.urls import url, include
from . import views

urlpatterns = [
    # 获取手机验证码
    url(r'^get_mobile_captcha/$', views.get_mobile_captcha, name="get_mobile_captcha"),
    # 获取图形验证码
    url(r'^get_captcha/$',views.get_captcha,name='get_captcha'),
    # 检查图形验证码
    url(r'^check_captcha/$',views.check_captcha,name='check_captcha'),
    # 题目列表接口
    url(r'^questions/$',views.questions,name='questions'),
    # 参考答案接口
    url(r'^answer/(?P<id>\d+)/',views.AnswerView.as_view(),name="answer"),
    # 其他答案接口
    url(r'^other_answer/(?P<id>\d+)/',views.OtherAnswerView.as_view(),name="answer"),
    # 收藏答案
    url(r'^answer/collection/(?P<id>\d+)/',views.AnswerCollectionView.as_view(),name="answer_collection"),
    # 收藏题目
    url(r'question/collection/(?P<id>\d+)/',views.QuestionsCollectionView.as_view(),name="quesionscollection"),
    # 上传图片
    url(r'^change_avator/$',views.ChangeAvator.as_view(),name='change_avator'),

    url(r"^question/$",views.Question.as_view(),name="question"),
]

