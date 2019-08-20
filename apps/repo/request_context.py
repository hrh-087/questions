from question_repo import settings
from .models import Answers
from libs.repo_data import user_answer_data


def global_data(request):
    no = 1
    site = {}
    site["SITE_NAME"] = settings.SITE_NAME

    if request.user.is_authenticated():
        user_data = user_answer_data(request.user)
        hot_question = Answers.objects.hot_question()
        hot_user = Answers.objects.hot_user()
    return locals()