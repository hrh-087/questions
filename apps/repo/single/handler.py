


from  django.dispatch import receiver
from  django.core.signals import request_finished
from django.db.models.signals import post_save
from .. models import Answers
from apps.repo.models import UserLog,QuestionsCollection,AnswersCollection
#注册信息
# @receiver(request_finished)
# def all_log(sender, **kwargs):
#     print(kwargs)
#     print(sender, "all log=>访问结束")

# post_save =>对象保存后
# sender => 指定发送信号的模型
@receiver(post_save,sender = Answers)
# def answer_log(sender,instance,created,row,using,update_fileds,**kwargs):
def answer_log(sender, instance, created,**kwargs):
    # instance => answer objevtct
    UserLog.objects.create(user=instance.user,operate=3,question=instance.question)


@receiver(post_save,sender=QuestionsCollection)
def question_collection_log(sender, instance, created,**kwargs):
    if instance.status:
        operate = 1
    else:
        operate = 2
    UserLog.objects.create(user=instance.user,operate=3,question=instance.question)

@receiver(post_save,sender=AnswersCollection)
def answer_collection(sender, instance, created,**kwargs):
    if instance.status:
        operate = 1
    else:
        operate = 2
    UserLog.objects.create(user=instance.user, operate=operate,answer=instance.answer)