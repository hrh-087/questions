from django.shortcuts import render
from . models import  Questions , Category,Answers,UserLog
from django.views.generic import View,DetailView
from django.http.response import JsonResponse
from django.core import serializers
from apps.accounts.models import User
from django.contrib.auth.decorators import login_required
from libs.repo_data import user_answer_data
from libs.dynamic_user import recent_answer, recent_user
import json
import random
import logging
logger = logging.getLogger("repo")


# Create your views here.

def login(request):
    return  render(request, "login.html")


def register(request):
    return  render(request, "register.html")


@login_required
def index(request):
    recent_answer = Answers.objects.order_by("-last_modify")[:10]
    kwgs = {
        "recent_answer": recent_answer,
        'recent_user': recent_user(),
        # "hot_user": Answers.objects.hot_user(),
        # 'hot_question': Answers.objects.hot_question(),
        # 'user_data': user_answer_data(request.user),
        }
    # print(Answers.objects.hot_question())
    return render(request, 'index.html', kwgs)



def questions(request):
    category = Category.objects.all()
    grades = Questions.DIF_CHOICES
    search = request.GET.get('search',"")
    kwgs = {'category':category,
            'grades':grades ,
            'search_key':search,
            }
    return  render(request, "questions.html",kwgs)

# class QuestionDedail(View):
#     def get(self ,request,question_id):
#         return  render(request,"question_detail.html")
class QuestionDetail(DetailView):
    model = Questions
    pk_url_kwarg = 'id'
    template_name = "question_detail.html"
    # 默认名：object
    context_object_name = "object"
    # 额外传递my_answers
    def get_context_data(self, **kwargs):
    # Answers.objects.get(user=request.user) => answerobject =>只适合取出有且只有一条的数据
    # Answers.objects.filter(user=request.user) => querySet =>能取出0-N条数据
    # kwargs :字典、字典中的数据返回给HTML页面
    # self.get_object() =>获取当前id的数据
        question = self.get_object()
        kwargs["my_answer"] = Answers.objects.filter(question=self.get_object(),user=self.request.user)
        kwargs["other_answer"] = Answers.objects.filter(question=self.get_object())
        return super().get_context_data(**kwargs)

    def post(self,request,id):
        from  django.db import  transaction
        try:
            # 增加事务 让回答和日志保持一致
            with transaction.atomic():
                # 没有回答过。create
                # 更新回答。get -> update
                # 获取对象，没有获取到直接创建对象
                new_answer = Answers.objects.get_or_create(question=self.get_object(),user=self.request.user)
                # 元组：第一个元素获取/创建的对象，True（新创建)/False(老数据)
                new_answer[0].answer = request.POST.get("answer","没有提交答案信息")
                new_answer[0].save()
                # raise ValueError("出错了")
                # 写日志
                # OPERATE = ((1, "收藏"), (2, "取消收藏"), (3, "回答"))
                # UserLog.objects.create(user=request.user,question=self.get_object(),operate=3)
                # serialize => 参数1：格式，参数2：可迭代对象 =>json字符串 => json->python-object
                my_answer = json.loads(serializers.serialize("json",[new_answer[0]]))[0]["fields"]
                msg = "提交成功"
                code = 200
        except Exception as ex:
            logger.error(ex)
            my_answer = {}
            msg = "提交失败"
            code = 500
        result = {"status": code,"msg": msg,"my_answer": my_answer}
        return JsonResponse(result)
"""
# 10个地方有 提交、更新答案的功能
index/
Answer.objects.creaet  #=》class Answer:def 



"""
def custom_404(request):
    return render(request, '404.html',status=404)

def custom_500(request):
    return render(request, '500.html', {"number":random.randint(10)},status=500)