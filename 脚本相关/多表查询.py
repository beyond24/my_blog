import datetime
import os
import random

# from faker import Faker
from django.db.models import Q

if __name__ == '__main__':
    # 加载Django项目的配置信息
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_blog.settings")
    # 导入Django，并启动Django项目
    import django

    django.setup()

    from userprofile.models import *
    from article.models import *
    from comment.models import *


    Comment.objects.filter().all().delete()