from django.shortcuts import render, redirect
from .models import TweetModel, TweetComment # 글쓰기 모델
from django.contrib.auth.decorators import login_required # 사용자가 로그인되어 있어야만 사용할 수 있음
from django.views.generic import ListView, TemplateView


# Create your views here.
def home(request):
    user = request.user.is_authenticated # 사용자가 로그인되어 있는지 확인
    if user:
        return redirect('/tweet')
    else:
        return redirect('/sign-in')

@login_required
def tweet(request):
    if request.method == 'GET':  # 요청하는 방식이 GET 방식인지 확인하기
        all_tweet = TweetModel.objects.all().order_by('-created_at')
        return render(request, 'tweet/home.html', {'tweet' : all_tweet})

    elif request.method == 'POST':  # 요청 방식이 POST 일때
        user = request.user  # 현재 로그인 한 사용자를 불러오기
        content = request.Post.get('my-content', '') # 글이 작성되지 않았다면 빈칸

        tags = request.POST.get('tag', '').split(',')
        if content == '':
            all_tweet = TweetModel.objects.all().order_by('-created_at')
            return render(request, 'tweet/home.html', {'error':'글은 공백일 수 없습니다.', 'tweet': all_tweet})
        else:
            my_tweet = TweetModel().objects.create(author=user, content=content)
            for tag in tags:
                tag = tag.strip()
                if tag != '':
                    my_tweet.tags.add(tag)
            my_tweet.save()
            return redirect('/tweet')


@login_required
def delete_tweet(request, id):
    my_tweet = TweetModel.objects.get(id=id)
    my_tweet.delete()
    return redirect('/tweet')

@login_required
def detail_tweet(request, id):
    my_tweet = TweetModel.objects.get(id=id)
    tweet_comment = TweetComment.objects.filter(tweet_id=id).order_by('-created_at')
    return render(request, 'tweet/tweet_detail.html', {'tweet':my_tweet, 'comment':tweet_comment})


@login_required
def write_comment(request, id):
    if request.method == 'POST':
        comment = request.POST.get("comment", "")
        current_tweet = TweetModel.objects.get(id=id)

        TC = TweetComment()
        TC.comment = comment
        TC.author = request.user
        TC.tweet = current_tweet
        TC.save()

        return redirect('/tweet/'+str(id))


@login_required
def delete_comment(request, id):
    comment = TweetComment.objects.get(id=id)
    current_tweet = comment.tweet.id
    comment.delete()
    return redirect('/tweet/'+str(current_tweet))

# 태그들을 모아놓는 태그 클라우드
class TagCloudTV(TemplateView):
    template_name = 'taggit/tag_cloud_view.html'

# 태그들을 모아서 화면에 전달하는 역할
class TaggedObjectLV(ListView):
    template_name = 'taggit/tag_with_post.html'
    model = TweetModel

    def get_queryset(self):
        return TweetModel.objects.filter(tags__name=self.kwargs.get('tag'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tagname'] = self.kwargs['tag']
        return context