from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Exists, OuterRef, Prefetch, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Post, Comment
from .forms import PostForm, CommentForm


def list__posts(request):
    posts = (
        Post.objects.published()
        .prefetch_related('categories')
        .select_related('author')
        .order_by('-created_at')
    )

    paginator = Paginator(posts, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'blog/list.html', {
        'posts': page_obj,
        'page_obj': page_obj,
        'page_range': paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1),
    })


def detail__post(request, date, cat, pk):
    post = get_object_or_404(
        Post.objects.published()
        .prefetch_related('categories')
        .select_related('author'),
        pk=pk
    )

    if request.path != post.get_absolute_url():
        return redirect(post, permanent=True)

    category_ids = [c.pk for c in post.categories.all()]
    
    related_articles = (
        Post.objects.published()
        .filter(categories__in=category_ids)
        .exclude(pk=post.pk)
        .annotate(shared_categories=Count('categories', filter=Q(categories__in=category_ids)))
        .order_by('-shared_categories', '-created_at')
        .select_related('author')
        .prefetch_related('categories')[:3]
    )

    has_active_reply = Exists(
        Comment.objects.filter(parent=OuterRef('pk'), is_active=True)
    )
    comments = (
        post.comments
        .filter(parent__isnull=True)
        .filter(Q(is_active=True) | Q(has_active_reply))
        .select_related('user')
        .prefetch_related(
            Prefetch(
                'replies',
                queryset=Comment.objects.filter(is_active=True).select_related('user')
            )
        )
    )

    return render(request, 'blog/detail.html', {
        'post': post,
        'related_articles': related_articles,
        'comments': comments,
        'comment_count': post.comments.filter(is_active=True).count(),
        'comment_form': CommentForm(),
    })


@login_required
@require_POST
def add_comment(request, pk):
    post = get_object_or_404(Post.objects.published(), pk=pk)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.user = request.user

        parent_id = request.POST.get('parent_id')
        if parent_id:
            parent = get_object_or_404(Comment, pk=parent_id, post=post, is_active=True)
            comment.parent = parent.parent or parent

        comment.save()
        return redirect(f'{post.get_absolute_url()}#comment-{comment.pk}')

    return redirect(f'{post.get_absolute_url()}#comments')


@login_required
@require_POST
def deactivate_comment(request, pk):
    comment = get_object_or_404(
        Comment.objects.select_related('post'),
        pk=pk, user=request.user, is_active=True
    )
    comment.is_active = False
    comment.save(update_fields=['is_active', 'updated_at'])

    return redirect(f'{comment.post.get_absolute_url()}#comments')



@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(
        Comment.objects.select_related('post'),
        pk=pk, user=request.user, is_active=True
    )

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.edited_at = timezone.now()
            comment.save()
            return redirect(f'{comment.post.get_absolute_url()}#comment-{comment.pk}')

    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/comment_edit.html', {
        'form': form,
        'comment': comment,
    })

def create__post(request):
    if request.method == "POST":
        form = PostForm(request.POST, user=request.user)

        if form.is_valid():
            post = form.save(commit=False)

            if request.user.is_authenticated:
                post.author = request.user

            post.is_verified = False
            post.save()
            form.save_m2m()

            return redirect('blog:success_page')

    else:
        form = PostForm(user=request.user)

    return render(request, 'blog/create.html', {
        'form': form
    })


def success_page__post(request):
    return render(request, 'blog/success.html')
