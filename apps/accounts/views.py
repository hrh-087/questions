from django.shortcuts import render, redirect, reverse, render_to_response,HttpResponse
from django.views.generic import View
from .forms import RegisterForm,LoginForm
from django.core.cache import cache
from django.contrib.auth.hashers import make_password
from .models import User,FindPassword
from django.contrib import auth
from  django.core.mail import send_mail
import logging
import random
import string
logger = logging.getLogger('account')
# Create your views here.

# if post
def register(request):
    return render(request, "accounts/register.html")


class Register(View):
    def get(self, request):
        "当是get请求的时候，执行此部分"
        form = RegisterForm()
        return render(request, "accounts/register.html", {"form":form})

    def post(self, request):
       "当是post请求的时候，执行此部分"
       form = RegisterForm(request.POST)
       ret = {}
       if form.is_valid():
           # 创建用户
           username = form.cleaned_data["username"]
           password = form.cleaned_data["password"]
           mobile = form.cleaned_data["mobile"]
           mobile_captcha = form.cleaned_data["mobile_captcha"]
           mobile_captcha_reids = cache.get(mobile)
           if mobile_captcha == mobile_captcha_reids:
               user = User.objects.create(username=username, password=make_password(password))
               user.save()
               ret['status'] = 200
               ret['msg'] = "注册成功"
               # 登录逻辑
               return redirect(reverse("accounts:login"))
           else:
               ret["status"] = 400
               ret['msg'] = "手机验证码有误"
       else:
           ret["status"] = 400
           ret["msg"] = "填入的用户名或密码不符合规范"
       return render(request, "accounts/register.html", {"form": form, "msg":ret})

class Login(View):
    # 当加载Login页面时
    def get(self,request):
        # 如果已登录，则直接跳转到首页（index）页面
        # request.user 表示时候当前登录的用户对象，
        if request.user.is_authenticated:
            return  redirect(reverse('repo:index'))
        form = LoginForm()
        # 设置下一跳转地址
        request.session['next'] = request.GET.get('next',reverse('repo:index'))
        return render(request,'accounts/login.html',{"form":form})

    # Form表单直接提交
    def post(self,request):
        # 表单数据绑定
        form = LoginForm(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")
        captcha = request.POST.get("captcha")
        session_captcha_code = request.session.get("captcha_code","")
        logger.debug(f"登录提交验证码:{captcha}-{session_captcha_code}")
        if captcha.lower() ==session_captcha_code.lower():
            user = auth.authenticate(username=username,password=password)
            if user is not None and user.is_active:
                auth.login(request,user)
                logger.info(f"{username}登录成功")
            # 跳转到next
                return redirect(request.session.get("next",'/'))
        msg = "用户名或密码错误"
        # logger.error(f"{username}登录失败")
        return render(request,"accounts/login.html",{"form": form,"msg": msg})

def logout(request):
    logger.info(request.user)
    auth.logout(request)
    return redirect(reverse('accounts:login'))


class PasswordForget(View):
    def get(self,request):
        return render(request, 'accounts/forget.html')

    def post(self,request):
        #  获取html页面上用户输入的email信息
        email = request.POST.get('email')
        # 判断html传过来的email是否有值，判断User表中是否有这个email
        if email and User.objects.filter(email=email):
            # 使用random生成一个用string拼接出来的一个随机字符串
            verify_code = "".join(random.choices(string.ascii_lowercase+string.digits,k=128))
            # request.Meta['HTTP_HOST']--->指定主机名，HTTP_HOST----》表示是当前主机
            url = f"{request.scheme}://{request.META['HTTP_HOST']}/accounts/password/reset/{verify_code}?email={email}"
            # 在FindPassword表中将email添加进去
            ret = FindPassword.objects.get_or_create(email=email)
            print(ret)
            ret[0].verify_code = verify_code
            ret[0].status = False
            ret[0].save()
            print("发邮件")
            # send_mail 的必填参数 1.邮件主题 2.邮件信息 3.电子邮件（没有选None）4.收件人邮箱
            send_mail("注册用户验证信息",url,None,[email])

            return HttpResponse('邮件发送成功，请登录邮箱查看！')
        else:
            msg = "输入的邮箱不存在！"
            return render(request, 'accounts/forget.html',{'msg':msg})

class PasswordReset(View):
    def get(self,request,verify_code):
        import datetime
        """需要判断时间"""
        # 计算出链接地址的有效时间
        crete_time_newer = datetime.datetime.utcnow()-datetime.timedelta(minutes=30)
        # 查看当前发送邮箱的时间以及验证码
        print(crete_time_newer,verify_code)
        email = request.GET.get("email")
        # find_password = FindPassword.objects.filter(status=False, verify_code=verify_code, creat_time__gte=create_time_newer, email=email)
        # 邮箱、verify_code、status=False、时间近30分钟
        print(crete_time_newer)
        find_passowrd = FindPassword.objects.filter(status=False,verify_code=verify_code,email=email,creat_time__gt=crete_time_newer)
        # find_passowrd = FindPassword.objects.filter(status=False,verify_code=verify_code,email=email)
        # 判断验证码是否有值，是否符合find_password条件
        print(verify_code)
        print(find_passowrd)
        print(crete_time_newer, find_passowrd[0].creat_time)
        if verify_code and find_passowrd:
            return render(request,'accounts/register.html')
        else:
            return HttpResponse("无效")

    def post(self,request,verify_code):
        # 获取html页面的password1
        password1 = request.POST.get("password1")
        # 获取html页面的password2
        password2 = request.POST.get("password2")
        if password1 == password2:
            try:
                find_password = FindPassword.objects.get(status=False,verify_code=verify_code)
                #  User中的email替换成Find_password中的email
                user = User.objects.get(email=find_password.email)
                # 修改密码
                user.set_password(password2)
                # 保存修改的密码
                user.save()
                #　返回的信息
                msg = "重置密码成功，请登录"
                find_password.status = True
                find_password.save()
            except Exception as ex:
                print(ex)
                msg = "出错了"
            return  render(request,"accounts/register.html",{"msg":msg})

