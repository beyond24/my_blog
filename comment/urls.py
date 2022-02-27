from django.urls import path

# 正在部署的应用的名称
from comment import views

app_name = 'comment'

urlpatterns = [
    path('post-comment/<int:article_id>', views.post_comment, name='post_comment'),

    # 二级评论
    path('post-comment/<int:article_id>/<int:parent_comment_id>', views.post_comment, name='comment_reply')
]
