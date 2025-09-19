from django.contrib import admin
from django.urls import path
from django.urls import include
from django.contrib.sitemaps.views import sitemap
from post.sitemaps import PostSitemap
from accounts import views as accounts_views
from post.views import explore, post_detail, add_post, like_post, add_comment, edit_profile, delete_post, edit_post, legacy_post_detail
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', accounts_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('login/', accounts_views.login, name='login'),
    path('signup/', accounts_views.signup, name='signup'),
    path('logout/', accounts_views.logout, name='logout'),
    path('explore/', explore, name='explore'),
    path('post/<slug:slug>/', post_detail, name='post_detail'),
    path('dashboard/', accounts_views.dashboard, name='dashboard'),
    path('add_post/', add_post, name='add_post'),
    path('post/<int:post_id>/like/', like_post, name='like_post'),
    path('post/<int:post_id>/comment/', add_comment, name='add_comment'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('delete_post/<int:post_id>/', delete_post, name='delete_post'),
    path('edit_post/<int:post_id>/', edit_post, name='edit_post'),
    path('terms/', accounts_views.terms, name='terms'),
    path('privacypolicy/', accounts_views.privacypolicy, name='privacypolicy'),
    path('post/<int:post_id>/', legacy_post_detail, name='legacy_post_detail'),
    path('sitemap.xml', sitemap, {'sitemaps': {'posts': PostSitemap}}, name='django_sitemap'),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
