from django.shortcuts import render, redirect
from .models import UserModel
from django.http import HttpResponse
from django.contrib.auth import get_user_model # 사용자가 데이터베이스 안에 있는지 검사하는 함수
from django.contrib import  auth # 사용자 auth 기능
from django.contrib.auth.decorators import login_required # 사용자가 로그인되어 있어야만 사용할 수 있음


# Create your views here.
# user/views.py
def sign_up_view(request):
    if request.method == 'GET':
        user = request.user.is_authenticated # 사용자가 로그인 되어 있는지 확인하는 변수
        if user:
            return redirect('/')
        else:
            return render(request, 'user/signup.html')
    elif request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        bio = request.POST.get('bio', '')

        if password != password2:
            # 패스워드가 같지 않다고 알람
            return render(request, 'user/signup.html', {'error':'패스워드를 확인해 주세요!'})
        else:
            if username == '' or password == '':
                return render(request, 'user/signup.html', {'error': '사용자 이름과 비밀번호는 필수값입니다.!'})

            exist_user = get_user_model().objects.filter(username=username)
            if exist_user:
                return render(request, 'user/signup.html', {'error':'사용자가 존재합니다.'})
            else:
                UserModel.objects.create_user(username=username, password=password, bio=bio)
                return redirect('/sign-in')


# user/views.py
def sign_in_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        me = auth.authenticate(request, username=username, password=password)  # 사용자 불러오기 / 암호화된 비밀번호를 맞는지 검사하는 기능
        if me is not None:  # 사용자 정보가 있는지 없는지 검사
            auth.login(request, me) # 장고가 로그인한 뒤 정보 저장
            return redirect('/')
        else: # 로그인이 실패하면 다시 로그인 페이지를 보여주기
            return render(request, 'user/signin.html', {'error':'유지이름 혹은 패스워드를 확인해주세요.'})

    elif request.method == 'GET':
        user = request.user.is_authenticated
        if user:
            return redirect('/')
        else:
            return render(request, 'user/signin.html')

@login_required # 사용자가 로그인이 되어 있어야만 접근이 가능한 함수
def logout(request):
    auth.logout(request) # 장고의 로그아웃 기능
    return redirect('/')



@login_required
def user_view(request):
    if request.method == 'GET':
        # 사용자를 불러오기, exclude와 request.user.username 를 사용해서 '로그인 한 사용자'를 제외하기
        user_list = UserModel.objects.all().exclude(username=request.user.username)
        return render(request, 'user/user_list.html', {'user_list': user_list})


@login_required
def user_follow(request, id):
    me = request.user
    click_user = UserModel.objects.get(id=id)
    if me in click_user.followee.all():
        click_user.followee.remove(request.user)
    else:
        click_user.followee.add(request.user)
    return redirect('/user')