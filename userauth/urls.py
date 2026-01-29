from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home,name='home'),
    path('signup/',views.signup, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('loginn/',views.loginnpage, name='loginn'),
    path('logout/',views.logoutpage, name='logout'),
    path('upload/',views.uploadpage, name='upload'),
    path('like-post/<str:id>', views.likepage, name='like-post'),
    path('#<str:id>', views.home_post),
    path('explore/',views.explorepage,name='explore'),
    path('profile/<str:id_user>', views.profilepage,name='profile'),
    path('follow/', views.followpage, name='followpage'),    
    path('delete/<str:id>', views.deletepage,name='delete'),
    path('search-results/', views.search_results, name='search_results'),
    path('account/', views.account, name='account'),
    path('chat/', include('userauth.chat.urls')),
    path('reels/', views.reels, name='reels'),
    path('add-comment/', views.add_comment, name='add_comment'),
    path('searched/', views.searched, name="search"),  
    path('forgetPassword/', views.forgetPassword, name='forget_Password'),
    path('newPasswordPage/<uidb64>/<token>/', views.newPasswordPage, name='new_password'), 
]
