from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse

from .forms import UserLoginForm, UserRegisterForm, ProfileForm
from django.contrib.auth.models import User

# 引入验证登录的装饰器
from django.contrib.auth.decorators import login_required

from .models import Profile


def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            # .cleaned_data 钩子后，清洗出合法数据
            data = user_login_form.cleaned_data
            # 检验账号、密码是否正确匹配数据库中的某个用户
            # 如果均匹配则返回这个 user 对象
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                # 将用户数据保存在 session 中，即实现了登录动作
                login(request, user)
                return redirect("article:article_list")
            else:
                user_login_form.add_error('password','请输入正确的帐号和密码！')
                context = {'form': user_login_form}
                return render(request, 'userprofile/login.html', context)
        else:
            context = {'form': user_login_form}
            return render(request, 'userprofile/login.html', context)
    elif request.method == 'GET':
        user_login_form = UserLoginForm()
        context = {'form': user_login_form}
        return render(request, 'userprofile/login.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")


def user_logout(request):
    logout(request)
    return redirect("article:article_list")


def user_register(request):
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)

        if not user_register_form.data['email']:
            user_register_form.add_error('email','请输入可用的邮箱，否则将无法找回密码')

        if user_register_form.is_valid():
            new_user = user_register_form.save(commit=False)
            # 设置密码
            new_user.set_password(user_register_form.cleaned_data['password'])
            new_user.save()
            # 保存好数据后立即登录并返回博客列表页面
            login(request, new_user)
            return redirect("article:article_list")
        else:
            context = {
                'form': user_register_form,
            }
            return render(request, 'userprofile/register.html', context)
    elif request.method == 'GET':
        user_register_form = UserRegisterForm()
        context = {
            'form': user_register_form,
        }
        return render(request, 'userprofile/register.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")


def user_delete(request, id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        # 验证登录用户、待删除用户是否相同
        if request.user == user:
            # 退出登录，删除数据并返回博客列表
            logout(request)
            user.delete()
            return redirect("article:article_list")
        else:
            return HttpResponse("你没有删除操作的权限。")
    else:
        return HttpResponse("仅接受post请求。")


# 编辑用户信息
@login_required(login_url='/userprofile/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)
    # user_id 是 OneToOneField 自动生成的字段
    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)



    if request.method == 'POST':
        profile_form = ProfileForm(request.POST,request.FILES)
        # 验证修改数据者，是否为用户本人
        if request.user != user:
            return HttpResponse("你没有权限修改此用户信息。")


        if profile_form.is_valid():
            # 取得清洗后的合法数据
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']

            if 'avatar' in request.FILES:
                profile.avatar = profile_cd["avatar"]

            profile.save()
            # 带参数的 redirect()
            return redirect("userprofile:edit", id=id)
        else:
            context = {
                'profile_form': profile_form,
                'profile': profile,
                'user': user
            }
            return render(request, 'userprofile/edit.html', context)

    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = {
            'profile_form': profile_form,
            'profile': profile,
            'user': user
        }
        return render(request, 'userprofile/edit.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")
