from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse



from post.models import Post

@login_required
def home(request):
    posts = Post.objects.filter(status="published").order_by('-created_at')[:1]  # latest 1 post
    total_posts = Post.objects.filter(status="published").count()
    from django.contrib.auth.models import User
    total_users = User.objects.count()
    # Featured author: most posts
    from django.db.models import Count
    author_stats = Post.objects.values('author__username').annotate(num_posts=Count('id')).order_by('-num_posts')
    featured_author = author_stats[0]['author__username'] if author_stats else None
    return render(request, 'home.html', {
        'posts': posts,
        'total_posts': total_posts,
        'total_users': total_users,
        'featured_author': featured_author,
    })


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = []
        if not username or not email or not password1 or not password2:
            errors.append('All fields are required.')
        if password1 != password2:
            errors.append('Passwords do not match.')
        if len(password1) < 6:
            errors.append('Password must be at least 6 characters long.')
        if User.objects.filter(username=username).exists():
            errors.append('Username already exists.')
        if User.objects.filter(email=email).exists():
            errors.append('Email already exists.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'signup.html')

        user = User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, 'Account created successfully.')
        auth_login(request, user)
        return redirect('dashboard')
    return render(request, 'signup.html')


def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return render(request, 'logout.html')


def login(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = None
        # Try to authenticate by username
        if User.objects.filter(username=username_or_email).exists():
            user = authenticate(request, username=username_or_email, password=password)
        # Try to authenticate by email
        elif User.objects.filter(email=username_or_email).exists():
            try:
                username = User.objects.get(email=username_or_email).username
                user = authenticate(request, username=username, password=password)
            except User.DoesNotExist:
                user = None
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Logged in successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username/email or password.')
            return render(request, 'login.html')
    return render(request, 'login.html')



def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user_posts = Post.objects.filter(author=request.user)
    total_posts = user_posts.count()
    published_posts = user_posts.filter(status="published").count()
    draft_posts = user_posts.filter(status="draft").count()
    recent_posts = user_posts.order_by('-created_at')[:5]
    total_comments = sum(post.comments.count() for post in user_posts)
    total_likes = sum(post.likes.count() for post in user_posts)
    # Use uploaded profile image if available, else fallback to ui-avatars
    profile_img_url = None
    try:
        if request.user.profile.image and request.user.profile.image.url:
            profile_img_url = request.user.profile.image.url
    except Exception:
        pass
    if not profile_img_url:
        profile_img_url = f"https://ui-avatars.com/api/?name={request.user.username}&background=0D8ABC&color=fff&size=80"
    return render(request, 'dashboard.html', {
        'user_posts': user_posts,
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'recent_posts': recent_posts,
        'total_comments': total_comments,
        'total_likes': total_likes,
        'profile_img_url': profile_img_url,
    })




def terms(request):
    return render(request, 'terms.html')   

def privacypolicy(request):
    return render(request, 'privacypolicy.html')