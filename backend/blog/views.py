"""Blog views: List and Detail pages."""
from django.shortcuts import render, get_object_or_404
from .models import BlogPost


def post_list(request):
    """Blog listing page with published posts."""
    posts = BlogPost.objects.filter(is_published=True)
    tag = request.GET.get('tag')
    if tag:
        posts = posts.filter(tags__icontains=tag)
    return render(request, 'blog/post_list.html', {'posts': posts, 'tag': tag})


def post_detail(request, slug):
    """Single blog post detail page with SEO meta tags."""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    # Get related posts
    related = BlogPost.objects.filter(
        is_published=True
    ).exclude(pk=post.pk)[:3]
    return render(request, 'blog/post_detail.html', {'post': post, 'related': related})
