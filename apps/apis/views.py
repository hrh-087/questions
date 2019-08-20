from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from libs.sms import send_sms
from io import BytesIO
import base64
from libs import patcha
from apps.repo.models import Questions,Answers,AnswersCollection,QuestionsCollection
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.template import loader, Context
from django.db import transaction
import os
import time
import datetime
from question_repo.settings import MEDIA_ROOT, MEDIA_URL
# Create your views here.

def get_mobile_captcha(request):
    # ret=> json格式 => {"code":200, "msg": "发送成功/发送失败/数据连接有误", "data": [1,2,3,4]}
    # mobile 手机号
    mobile = request.GET.get("mobile")
    if not mobile:
        # 400表示用户填写数据有误
        ret = {"code":400, "msg": "手机号有误"}
    else:
        # 生成手机验证码(6位0-9的数字组成)
        import random
        mobile_captcha = "".join(random.choices('0123456789', k=6))
        print(mobile_captcha)
        # 将验证码写入cacha->redis(300s过期)
        from django.core.cache import cache
        cache.set(mobile, mobile_captcha, 300)

        # 发送短信
        if send_sms(mobile, mobile_captcha):
            ret = {"code": 200, "msg": "发送成功"}
        else:
            ret = {"code": 500, "msg": "发送短信失败"}

    # 返回Json数据
    return JsonResponse(ret)

def get_captcha(request):
    # PIL 创建图片
    # 图形非常小、非常多、临时使用
    # 存放到内存 => data:
    # 直接在内存开辟一点空间存放临时生成的图片
    f = BytesIO()
    # 调用check_code生成照片和验证码
    img, code = patcha.create_validate_code()
    # 将验证码存在服务器的session中，用于校验
    request.session['captcha_code'] = code
    # 生成的图片放置于开辟的内存中
    img.save(f,'PNG')
    # 将内存的数据读取出来，并以HttpResponse返回
    # return HttpResponse(f.getvalue())
    ret_type = "data:image/jpg;base64,".encode()
    ret = ret_type + base64.encodebytes(f.getvalue())
    del f
    return HttpResponse(ret)


def check_captcha(request):
    pass

def questions(request):
    # 获取参数
    pagestze = int(request.GET.get("limit",10))# 一次性去多少条数据
    offset = int(request.GET.get("offset",0))
    page = int(request.GET.get('page',1))
    grade = int(request.GET.get('grade',0))
    status = int(request.GET.get('status',2))
    # 2: 不筛选 1，已刷  0，待刷
    category = int(request.GET.get('category',0))
    search = request.GET.get("search","")
    # 取出所有数据e
    questions_list = Questions.objects.exclude(status=False)
    if search:
        questions_list = questions_list.filter(Q(id=search) | Q(content__icontains=search) | Q(title__icontains=search) )

    if grade: questions_list = questions_list.filter(grade=grade)
    if category: questions_list = questions_list.filter(category_id=category)

    questions_list = questions_list.values('id','title','grade','answer')
    total = len(questions_list)

    # 计算当前页面的数据
    questions_list = questions_list[offset:offset+pagestze]
    for item in questions_list:
        item["collection"] = True if QuestionsCollection.objects.filter(
            user=request.user, status=True, question_id=item['id']) else False
    questions_dict = {'total':total,'rows':questions_list}

    return JsonResponse(questions_dict)


class AnswerView(LoginRequiredMixin, View):
    """参考答案"""
    def get(self, request, id):
        # answer = Questions.objects.get(id=id)
        my_answer = Answers.objects.filter(question=id, user=request.user)
        if not my_answer:
            question = {"answer": "请回答后再查看参考答案"}
            return JsonResponse(question, safe=False)# safe是把除字典以外的格式转换成Json格式

        try:
            # model_to_dict适合Model-Object
            # serializers适合queryset
            # question = model_to_dict(Questions.objects.get(id=id))
            # question = serializers.serialize('json', Questions.objects.filter(id=id))
            # question = serializers.serialize('json', Questions.objects.filter(id=id))
            question = Questions.objects.filter(id=id).values()[0]
        except Exception as ex:
            print(ex)
            question = None
        return JsonResponse(question, safe=False)

class OtherAnswerView(LoginRequiredMixin, View):
    def get(self, request, id):
        # other_answer = list(Answers.objects.filter(question=id).values())
        # other_answer = serializers.serialize('json', Answers.objects.filter(question=id))
        # return JsonResponse(other_answer, safe=False)

        my_answer = Answers.objects.filter(question=id, user=request.user)
        if not my_answer:
            html = "请回答后再查看其他答案"
            return HttpResponse(html)

        # other_answer = Answers.objects.filter(question=id).exclude(user=request.user)
        other_answer = Answers.objects.filter(question=id)
        # print('hello')

        if other_answer:
            for answer in other_answer:
                if AnswersCollection.objects.filter(answer=answer, user=request.user, status=True):
                    answer.collect_status = 1 # => 控制爱心=>空心/实心
                # 外键 AnswersCollectionObject.answer=>related_name
                # answer被收藏哪些人收藏了
                # answer.answers_collection_set.filter(status=True)

                answer.collect_nums = answer.answers_collection_set.filter(status=True).count()
                # answer.answers_collection_set
            # 通过后端渲染出HTML
            # html = loader.render_to_string('question_detail_other_answer.html', {"other_answer": other_answer})
            html = loader.get_template('question_detail_other_answer.html').render({"other_answer": other_answer})
            # print(html)
        else:
            html = "暂无回答"
        return HttpResponse(html)

from django.forms.models import model_to_dict
import logging
logger = logging.getLogger("apis")

class AnswerCollectionView(LoginRequiredMixin, View):
    def get(self, request, id):
        try:
            answer = Answers.objects.get(id=id)
            with transaction.atomic():
                result = AnswersCollection.objects.get_or_create(user=request.user, answer=answer)
                # result = AnswersCollection.objects.get_or_create(user=request.user, answer_id=1)
                # True表示新创建,False表示老数据
                answer_collection = result[0]
                if not result[1]:
                    # 老数据
                    # print('x',answer_collection.status)
                    # True改False , False改True
                    if answer_collection.status: answer_collection.status=False
                    else: answer_collection.status=True
                answer_collection.save()
            msg = model_to_dict(answer_collection)
            # logger.info(msg)
            msg["collections"] = answer.answers_collection_set.filter(status=True).count()
            ret_info = {"code":200, "msg":msg}
        except Exception as ex :
            ret_info = {"code":500,"msg":[]}
        # print(ret_info)
        return JsonResponse(ret_info)
        # return HttpResponse('abc')
class QuestionsCollectionView(LoginRequiredMixin, View):
        def get(self,request,id):
            try:
                question = Questions.objects.get(id=id)
                with transaction.atomic():

                    result = QuestionsCollection.objects.get_or_create(user=request.user , question= question)
                # print(result)
                    question_collection = result[0]
                # print(question_collection)
                # True表示新创建,False表示老数据
                # question_collection = result[0]
                    if not result[1]:
                        # 老数据
                        # print('x',answer_collection.status)
                        # True改False , False改True
                        if question_collection.status:question_collection.status = False
                        else:question_collection.status = True
                    question_collection.save()
                    msg = model_to_dict(question_collection)
                    # logger.info(msg)
                    ret_info = {"code":200, "msg":msg}
            except Exception as  ex:
                ret_info = {"code":500,"msg":[]}
            return JsonResponse(ret_info)

class ChangeAvator(LoginRequiredMixin, View):
    def post(self, request):
        # 时间的格式
        today = datetime.date.today().strftime("%Y%m%d")
        # 图片的data-img格式
        img_src_str = request.POST.get("image")
        img_str = img_src_str.split(',')[1]
        # 取出格式
        img_type = img_src_str.split(';')[0].split('/')[1]
        # 取出数据
        img_data = base64.b64decode(img_str)
        # 相对上传路径
        avator_path = os.path.join("avator", today)
        # 绝对上传路径
        avator_path_full = os.path.join(MEDIA_ROOT, avator_path)
        if not os.path.exists(avator_path_full):
            os.mkdir(avator_path_full)
        filename = str(time.time()) + "." + img_type
        # 绝对文件路径，用于保存图片
        filename_full = os.path.join(avator_path_full, filename)
        # 相对MEDIA_URL路径，用于展示数据
        img_url = f"{MEDIA_URL}{avator_path}/{filename}"
        try:
            with open(filename_full, 'wb') as fp:
                fp.write(img_data)
                ret = {
                    "result": "ok",
                    "file": img_url
                }
        except Exception as ex:
            ret = {
                "result": "error",
                "file": "upload fail"
            }
        request.user.avator_sor = os.path.join(avator_path, filename)
        request.user.save()
        return JsonResponse(ret)

class Question(LoginRequiredMixin,View):
    def post(self,request):
        print(request.POST)
        try:
            title = request.POST.get("title")
            category = request.POST.get("category")
            content = request.POST.get("content")
            if category:
                Questions.objects.create(title=title,category_id=category,content=content,contributor=request.user)
            else:
                Questions.objects.create(title=title,content=content,contributor=request.user)
        except Exception as x:
            logger.error(x)
            return HttpResponse("提交失败！")
        return HttpResponse("提交成功")