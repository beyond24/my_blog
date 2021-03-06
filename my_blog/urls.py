"""my_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path

from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from article.views import article_list, page_not_found

urlpatterns = [
    path('', article_list, name='home'),
    # 启用media
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}, name='media'),

    path('admin/', admin.site.urls),
    # 文章
    path('article/', include('article.urls', namespace='article')),

    # 评论
    path('comment/', include('comment.urls', namespace='comment')),

    # 用户
    path('userprofile/', include('userprofile.urls', namespace='userprofile')),

    # 引用轮子
    # 密码重置
    path('password-reset/', include('password_reset.urls')),
    # 通知
    path('inbox/notifications/', include('notifications.urls', namespace='notifications')),
    path('notice/', include('notice.urls', namespace='notice')),
]
handler404 = page_not_found