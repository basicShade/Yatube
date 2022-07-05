from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from core.utils import get_page_obj
from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

POSTS_PER_PAGE_LIMIT = 10
POST_PREVIEW_LEN_WORDS = 10
VISIBLE_COMMENTS_LIMIT = 10


@cache_page(20)
def index(request):
    """Главная страница"""
    posts_list = Post.objects.select_related('group', 'author')
    page_obj = get_page_obj(posts_list, POSTS_PER_PAGE_LIMIT, request)

    context = {
        'page_obj': page_obj,
        'post_trunc': POST_PREVIEW_LEN_WORDS,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Страница сообщества"""
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    page_obj = get_page_obj(posts_list, POSTS_PER_PAGE_LIMIT, request)

    context = {
        'group': group,
        'page_obj': page_obj,
        'post_trunc': POST_PREVIEW_LEN_WORDS,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = User.objects.get(username=username)
    posts_list = author.posts.select_related('group')
    posts_count = posts_list.count
    page_obj = get_page_obj(posts_list, POSTS_PER_PAGE_LIMIT, request)
    following = None
    if request.user.is_authenticated and request.user != author:
        following = Follow.objects.filter(user=request.user, author=author)

    context = {
        'author': author,
        'page_obj': page_obj,
        'posts_count': posts_count,
        'post_trunc': POST_PREVIEW_LEN_WORDS,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('group', 'author'),
        id=post_id
    )
    posts_count = post.author.posts.count
    add_comment_form = CommentForm()
    comments = Comment.objects.filter(post=post)[:VISIBLE_COMMENTS_LIMIT]

    context = {
        'post': post,
        'posts_count': posts_count,
        'add_comment_form': add_comment_form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', username=form.author)

    groups = Group.objects.all()
    context = {
        'form': form,
        'groups': groups,
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:post_detail', post_id=post.id)

    groups = Group.objects.all()
    context = {
        'form': form,
        'groups': groups,
        'is_edit': True
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Страница с подписками"""
    posts_list = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page_obj(posts_list, POSTS_PER_PAGE_LIMIT, request)

    context = {
        'page_obj': page_obj,
        'post_trunc': POST_PREVIEW_LEN_WORDS,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    following = Follow.objects.filter(user=request.user, author=author)
    if request.user != author and not following:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=author)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=author)
