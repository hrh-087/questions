from apps.repo.models import Answers, User, Questions
from django.db.models import Count

def check_rank(data):
    return data["id__count"]

def user_answer_data(user):
    # 答题数量及总量
    # count=> 计数
    # 统计回答了多少个题目
    answer_num = Answers.objects.filter(user=user).count()
    # 统计Qestions总共有多少个题目
    question_all = Questions.objects.all().__len__()
    # 用户总量
    user_sum = User.objects.all().__len__()
    # 答题情况
    # 每个用户答题数量:按用户统计答题数量
    rank = Answers.objects.values('user').annotate(Count('id'))
    # <QuerySet [{'user': 1, 'id__count': 1}, {'user': 2, 'id__count': 1}, {'user': 3, 'id__count': 2}]>
    # print(rank) 按答题量排序
    rank = sorted(rank, key=check_rank, reverse=True)

    # 统计每个人的排名(为提升效率，可写入memcache)
    rank_dict = {}
    cur_rank = 0
    cur_count = 0
    for index, item in enumerate(rank, start=1):
        if cur_count != item["id__count"]:
            cur_rank = index
        cur_count = item["id__count"]
        rank_dict[item["user"]] = dict(item, **{"rank":cur_rank})
    print(rank_dict)
    kwgs = {
        "answer_num": answer_num,
        "question_all": question_all,
        "user_sum": user_sum,
        "rank": rank_dict[user.id] if answer_num else {"rank":0, },
    }
    return kwgs

