from django.http import HttpResponseRedirect

def legacy_post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return HttpResponseRedirect(post.get_absolute_url())
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.text import slugify
from .models import Post, Category, Tag, Like, Comment
from django.contrib.auth.models import User
from accounts.models import Profile
from accounts.forms import ProfileForm
from django.views.decorators.http import require_POST

@login_required
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')[:5]
    return render(request, 'post/post_list.html', {'posts': posts})



def explore(request):
    posts = Post.objects.filter(status="published").order_by('-created_at')
    return render(request, 'explore.html', {'posts': posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.increment_views()
    meta_description = post.summary if hasattr(post, 'summary') and post.summary else post.title
    meta_keywords = ', '.join([tag.name for tag in post.tags.all()])
    return render(request, 'post_detail.html', {
        'post': post,
        'likes_count': post.likes_count(),
        'comments_count': post.comments_count(),
        'meta_description': meta_description,
        'meta_keywords': meta_keywords,
    })


@login_required
def add_post(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        summary = request.POST.get('summary', '').strip()
        content = request.POST.get('content', '').strip()
        category_id = request.POST.get('category')
        tags_str = request.POST.get('tags', '').strip()
        status = request.POST.get('status', 'draft')
        image = request.FILES.get('image')
        date = request.POST.get('date')

        # Validation
        if not title:
            messages.error(request, "Title is required.")
            return redirect('add_post')
        if not summary:
            messages.error(request, "Summary is required.")
            return redirect('add_post')
        if not content:
            messages.error(request, "Content is required.")
            return redirect('add_post')

        # Generate unique slug
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while Post.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Handle category
        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                messages.error(request, "Selected category does not exist.")
                return redirect('add_post')

        # Create post
        post = Post(
            title=title,
            summary=summary,
            content=content,
            author=request.user,
            category=category,
            image=image if image else None,
            status=status,
            slug=slug
        )
        if date:
            post.created_at = date
        post.save()

        # Assign tags (comma separated)
        if tags_str:
            tag_list = [t.strip() for t in tags_str.split(',') if t.strip()]
            for tag_name in tag_list:
                tag_obj, created = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag_obj)

        messages.success(request, "Post created successfully!")
        return redirect('post_detail', slug=post.slug)
    return render(request, 'add_post.html')


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        messages.error(request, "You cannot like your own post.")
        return redirect('post_detail', slug=post.slug)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        messages.info(request, "You have already liked this post.")
    else:
        messages.success(request, "You liked this post!")
    return redirect('post_detail', slug=post.slug)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        text = request.POST.get('comment', '').strip()
        if text:
            Comment.objects.create(post=post, author=request.user, text=text)
    return redirect('post_detail', slug=post.slug)


# Update dashboard logic to show likes, views, comments
@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user_posts = Post.objects.filter(author=request.user)
    total_posts = user_posts.count()
    published_posts = user_posts.filter(status="published").count()
    draft_posts = user_posts.filter(status="draft").count()
    recent_posts = user_posts.order_by('-created_at')[:5]
    total_comments = Comment.objects.filter(post__author=request.user).count()
    return render(request, 'dashboard.html', {
        'user_posts': user_posts,
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'recent_posts': recent_posts,
        'total_comments': total_comments,
    })



@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = []
        if username:
            request.user.username = username
        if email:
            request.user.email = email
        if password1 or password2:
            if password1 != password2:
                errors.append('Passwords do not match.')
            elif len(password1) < 6:
                errors.append('Password must be at least 6 characters long.')
            else:
                request.user.set_password(password1)
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'edit_profile.html', {'user': request.user})
        request.user.save()
        messages.success(request, "Profile updated successfully!")
        if password1 and not errors:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
        return redirect('dashboard')
    return render(request, 'edit_profile.html', {'user': request.user})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully!")
        return redirect('dashboard')
    return render(request, 'delete_post.html', {'post': post})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        post.title = request.POST.get('title', '').strip()
        post.summary = request.POST.get('summary', '').strip()
        post.content = request.POST.get('content', '').strip()
        post.status = request.POST.get('status', post.status)
        # Handle tags
        tags_str = request.POST.get('tags', '').strip()
        if tags_str:
            tag_list = [t.strip() for t in tags_str.split(',') if t.strip()]
            post.tags.clear()
            for tag_name in tag_list:
                tag_obj, created = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag_obj)
        # Handle image
        image = request.FILES.get('image')
        if image:
            post.image = image
        post.save()
        messages.success(request, "Post updated successfully!")
    return render(request, 'edit_post.html', {'post': post})
    return redirect('post_detail', slug=post.slug)
    

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Update user profile information
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        # Add more fields as necessary

        if username:
            request.user.username = username
        if email:
            request.user.email = email
        request.user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('dashboard')
    return render(request, 'edit_profile.html', {'user': request.user})