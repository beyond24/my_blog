from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,redirect

# Create your views here.
from django.views import View
from django.views.generic import ListView

# LoginRequiredMixin混入类验证是否登录
from article.models import ArticlePost


class CommentNoticeListView(LoginRequiredMixin,ListView):
    """通知列表"""

    context_object_name = 'notices'
    template_name = 'notice/list.html'
    # 登录重定向路由
    login_url = 'userprofile/login/'

    def get_queryset(self):
        """处理查询集"""
        return self.request.user.notifications.unread()


class CommentNoticeUpdateView(View):
    """更新通知状态"""
    def get(self, request):
        # 获取未读消息
        notice_id = request.GET.get('notice_id')
        if notice_id:
            article = ArticlePost.objects.get(id=request.GET.get('article_id'))
            # notifications内置函数，标记一条notice为已读
            request.user.notifications.get(id=notice_id).mark_as_read()
            return redirect(article)    # redirect model对象时,model中需要有get_absolute_url方法
        # 点击清空全部按钮
        else:
            request.user.notifications.mark_all_as_read()
            return redirect('notice:list')


