from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
# Create your views here.
from notifications.signals import notify

from article.models import ArticlePost
from .forms import CommentForm
from .models import Comment


@login_required(login_url='/userprofile/login/')
def post_comment(request, article_id, parent_comment_id=None):
    article = get_object_or_404(ArticlePost, id=article_id)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.user = request.user

            # 二级回复
            if parent_comment_id:
                parent_comment = Comment.objects.get(id=parent_comment_id)
                # 若回复层级超过二级，则转换为二级
                new_comment.parent_id = parent_comment.get_root().id
                # 被回复人
                new_comment.reply_to = parent_comment.user
                new_comment.save()

                # 二级以上评论给被评论者发送消息
                if parent_comment.user_id != request.user.id:
                    notify.send(
                        request.user,
                        recipient=parent_comment.user,
                        verb='回复了你',
                        target=article,
                        action_object=new_comment,
                    )

                return JsonResponse({"code": "200 OK", "new_comment_id": new_comment.id})

            new_comment.save()

            # 一级评论给文章作者发送通知
            if request.user.id != article.author_id:
                notify.send(
                    request.user,
                    recipient=User.objects.filter(id=article.author_id),
                    verb='回复了你',
                    target=article,
                    action_object=new_comment,
                )

            return redirect(article)
            # redirect()：返回到一个适当的url中：即用户发送评论后，重新定向到文章详情页面。当其参数是一个Model对象时，会自动调用这个Model对象的get_absolute_url()方法
        else:
            return HttpResponse('表单有误')

    # 处理 GET 请求用于加载iframe
    elif request.method == 'GET':
        comment_form = CommentForm()
        context = {
            'comment_form': comment_form,
            # 传入事件的两个参数到template，再由前端ajax请求提交至数据库
            'article_id': article_id,
            'parent_comment_id': parent_comment_id
        }
        return render(request, 'comment/reply.html', context)

    else:
        return HttpResponse('评论仅支持post请求！')
