from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$',views.index,name="index"),
    url(r'^questions/$',views.questions,name="questions"),
    # url(r'^question_detail/(\d+)/$',views.QuestionDetail.as_view(),name="question_detail"),
    url(r'^question_detail/(?P<id>\d+)/$',views.QuestionDetail.as_view(),name="question_detail"),

]

