import datetime
import math

from django.utils import timezone

from django import template

# register模块级变量，它是一个 template.Library 实例，所有的filters均在其中注册
register = template.Library()



@register.filter(name='timesince_zh')
def time_since_zh(value):
    """获取更加人性化的时间，如x天前，x个月前"""
    now = timezone.now()    # <class 'datetime.datetime'>
    diff = now - value  # <class 'datetime.timedelta'>

    if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
        return '刚刚'

    if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
        return str(math.floor(diff.seconds / 60)) + "分钟前"   # math.floor向下取整

    if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
        return str(math.floor(diff.seconds / 3600)) + "小时前"

    if diff.days >= 1 and diff.days < 30:
        return str(diff.days) + "天前"

    if diff.days >= 30 and diff.days < 365:
        return str(math.floor(diff.days / 30)) + "个月前"

    if diff.days >= 365:
        return str(math.floor(diff.days / 365)) + "年前"

