from apps.repo.models import Answers
from apps.accounts.models import User
from django.db.models import Count

def recent_user():
    """最近刷题的同学"""
    # 按用户统计刷题的数量（新刷的在后面）
    result = Answers.objects.values_list('user').annotate(Count('id'))
    user_id_list = [item[0] for item in result][-10:]
    userlist = User.objects.filter(id__in=user_id_list)
    return userlist


def recent_answer():
    """最新刷题动态"""
    answers = Answers.objects.order_by("-last_modify")[:10]
    return answers