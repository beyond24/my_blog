import markdown
from django.contrib.auth.decorators import login_required,permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, HttpResponse,get_object_or_404

from comment.forms import CommentForm
from comment.models import Comment
from .models import ArticlePost, ArticleColumn
from django.contrib.auth.models import User
from .forms import ArticlePostForm
from django.contrib.admin.views.decorators import staff_member_required


# Create your views here.


def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')

    # 初始化查询集
    article_list = ArticlePost.objects.all()

    if search:
        # icontains不区分大小写，对应的contains区分大小写
        article_list = ArticlePost.objects.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search) |
            Q(comments__body__icontains=search)
        ).distinct()    #去重
    else:
        search = ''

    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    # 查询集排序
    if order == 'total_views':
        article_list = ArticlePost.objects.all().order_by('-total_views')

    # 每页显示 1 篇文章
    paginator = Paginator(article_list, 3)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)

    context = {
        'articles': articles,
        'order': order,
        'search': search,
        'column': column,
        'tag': tag,
    }
    return render(request, 'article/list.html', context)


def article_detail(request, id):
    article = get_object_or_404(ArticlePost, id=id)
    comments = Comment.objects.filter(article=id)

    comment_form = CommentForm()

    article.total_views += 1
    article.save(update_fields=['total_views'])
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)
    context = {
        'article': article,
        'toc': md.toc,
        'comments': comments,
        'comment_form': comment_form,
    }

    return render(request, 'article/detail.html', context)

@login_required(login_url='/userprofile/login/')
def article_create(request):
    if not request.user.is_superuser:
        return HttpResponse('你没有此权限！')
    if request.method == 'POST':
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)

            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.author = User.objects.get(id=request.user.id)
            new_article.save()
            # 保存tags的多对多关系
            article_post_form.save_m2m()
            return redirect('article:article_list')
        else:
            context = {
                'article_post_form': article_post_form,
            }
            return render(request, 'article/create.html', context)
    # 如果用户请求获取数据
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()

        context = {
            'article_post_form': article_post_form,
            'columns': columns,
        }

        return render(request, 'article/create.html', context)


@login_required(login_url='/userprofile/login/')
def article_delete(request, id):
    article = ArticlePost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权删除这篇文章。")
    article.delete()
    return redirect('article:article_list')


@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    article = ArticlePost.objects.get(id=id)

    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")

    if request.method == 'POST':
        article_post_form = ArticlePostForm(request.POST,request.FILES,instance=article)
        if article_post_form.is_valid():
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None

            article.tags.set(request.POST.get('tags').split(','), clear=True)
            article.save()
            return redirect("article:article_detail", id=id)
        # 不合法
        else:
            columns = ArticleColumn.objects.all()
            context = {
                'article': article,
                'article_post_form': article_post_form,
                'columns': columns,
                'tags': ','.join([x for x in article.tags.names()])
            }
            return render(request, 'article/update.html', context)
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        avatar = ArticlePost.objects.get(id=id)
        context = {
            'article': article,
            'article_post_form': article_post_form,
            'columns': columns,
            'tags': ','.join([x for x in article.tags.names()])
        }
        return render(request, 'article/update.html', context)
