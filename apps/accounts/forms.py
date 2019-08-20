



"""
注册表单：
    表单：用户名、手机号、2个密码、验证码
    - 添加用户名检查：用户名不能重复
    - 添加手机号检查：手机号不能重复
    - 添加密码检查：密码复杂度及两次密码一致
"""

from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from .models import User
from django.contrib.auth.hashers import check_password as auth_check_password

# 用户注册
class RegisterForm(forms.Form):
    username = forms.CharField(label="用户名", max_length="24", widget=widgets.TextInput(attrs={"class":"form-control", "placeholder": "请输入用户名"}))
    mobile = forms.CharField(label="手机号", max_length="24",widget=widgets.TextInput(attrs={"class":"form-control", "placeholder": "请输入手机号"}))
    password = forms.CharField(label="密 码", widget=widgets.PasswordInput(attrs={"class":"form-control", "placeholder": "请输入密码"}))
    password2 = forms.CharField(label="密 码2", widget=widgets.PasswordInput(attrs={"class":"form-control", "placeholder": "请再输入密码"}))
    mobile_captcha = forms.CharField(label="验证码", widget=widgets.TextInput(attrs={"style":"width: 160px;padding: 10px", "placeholder":"验证码", "error_messages": {"invalid": "验证码错误"}}))

    def clean_username(self):
        ret = User.objects.filter(username=self.cleaned_data.get("username"))
        if not ret:
            return self.cleaned_data.get("username")
        else:
            raise ValidationError("用户名已注册")

    def clean_mobile(self):
        ret = User.objects.filter(mobile=self.cleaned_data.get("mobile"))
        if not ret:
            return self.cleaned_data.get("mobile")
        else:
            raise ValidationError("手机号已绑定")

    def clean_password(self):
        data = self.cleaned_data.get("password")
        if not data.isdigit():
            return self.cleaned_data.get("password")
        else:
            raise ValidationError("密码不能全是数字")

    def clean(self):
        if self.cleaned_data.get("password") == self.cleaned_data.get("password2"):
            return self.cleaned_data
        else:
            raise ValidationError("两次密码不一致")

# 用户登录

class LoginForm(forms.ModelForm):
    # 定义一个验证码的字段
    # widget是设置一个小部件，widgets.TextInput是设置文本类型，attrs是设置字段的样式
    captcha = forms.CharField(label="验证码",widget=widgets.TextInput(attrs={
        "style":"width:160px;padding: 10px","placeholder":"验证码","onblur":"check_captcha",
        "error_massages":{"invalid":"验证码错误"}
    }))

    class Meta:
        model = User
        fields = ['username','password']
        widgets = {
            'username':widgets.TextInput(attrs={'class':'form-control','placeholder':"用户名"}),
            'password':widgets.PasswordInput(attrs={'class':'form-control','placeholder':'密码'})
        }

        def check_password(self):
            print('check_password')
            username = self.cleaned_data['username']
            password = self.cleaned_data['password']
            try:
                user = User.objects.get(username=username)
                return user,auth_check_password(password,user.password)
            except:
                return None,False

# 重置密码
class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)