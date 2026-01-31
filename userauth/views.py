from urllib import request
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse, JsonResponse, QueryDict
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.views import View
from . models import  Likepost, Profile 
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from . models import Post ,Likepost,Followers
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.db.models.signals import post_save
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from .models import Post, Comment,Reel
import re

def signup(request):
    if request.method == 'POST':
        uname = request.POST.get('fnm')
        email = request.POST.get('emailid')
        pass1 = request.POST.get('pwd')
        pass2 = request.POST.get('cpwd')
    
        if " " in uname:
            return render(request, 'signup.html', {'invalid': "Username must not contain spaces"})
        
        if not re.match(r"^[A-Za-z0-9_#@!$]+$", uname):
            return render(request, 'signup.html', {'invalid': "Username can contain only letters, numbers and underscore"})
        
        if not re.match(r'^[A-Z](?=.*\d)[A-Za-z0-9]{5,}$', pass1):
            return render(request,'signup.html',{'invalid': "Password must start with a capital letter, contain at least one number, and have no spaces or special characters."})
        if User.objects.filter(username=uname).exists():
            return render(request, 'signup.html', {'invalid': "Username already exists"})

        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'invalid': "Email already in use"})

        if pass1 != pass2:
            return render(request, 'signup.html', {'invalid': "Passwords do not match"})

        user = User.objects.create_user(
            username=uname,
            email=email,
            password=pass1
        )
        user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verify_link = f"http://{request.get_host()}/activate/{uid}/{token}/"
       
        send_mail(
            subject="Verify your Linkup Social Media account",
            message=f"Hello {user.username},\n\nVerify your account:\n{verify_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
            html_message = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verify Account</title>
</head>

<body style="margin:0; padding:0; background-color:#0f0f0f; font-family:Arial, sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0f0f0f; padding:20px;">
    <tr>
      <td align="center">

        <!-- Main Container -->
        <table width="100%" cellpadding="0" cellspacing="0" 
               style="max-width:600px; background-color:#111111; border-radius:16px; padding:30px;">

          <!-- Header -->
          <tr>
            <td align="center" style="padding-bottom:20px;">
              <h2 style="margin:0; color:#ffffff;">Linkup Social Media</h2>
            </td>
          </tr>

          <!-- Greeting -->
          <tr>
            <td style="color:#d1d5db; font-size:16px; padding-bottom:10px;">
              Hello <b>{user.username}</b>,
            </td>
          </tr>

          <!-- Message -->
          <tr>
            <td style="color:#d1d5db; font-size:16px; padding-bottom:20px;">
              Click the button below to verify your account:
            </td>
          </tr>

          <!-- Button Box -->
          <tr>
            <td align="center" style="padding:25px; background-color:#1c1c1c; border-radius:14px;">
              <a href="{verify_link}"
                 style="
                   display:inline-block;
                   padding:14px 32px;
                   background-color:#10a37f;
                   color:#ffffff;
                   text-decoration:none;
                   border-radius:10px;
                   font-size:18px;
                   font-weight:bold;
                 ">
                Verify Account
              </a>
            </td>
          </tr>

          <!-- Warning -->
          <tr>
            <td style="color:#9ca3af; font-size:14px; padding-top:20px;">
              Please ignore this email if this wasn’t you trying to create a
              <b>Linkup Social Media</b> account.
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="color:#9ca3af; font-size:14px; padding-top:20px;">
              Thanks,<br>
              <b>Linkup Social Media Team</b>
            </td>
          </tr>

        </table>
        <!-- End Main Container -->

      </td>
    </tr>
  </table>

</body>
</html>
"""
        )
        return render(request, 'signup.html', {
            'messages': ["Your Account Created Successfully. Please check your email to verify your account."]
        })
    return render(request, 'signup.html')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save() 
        return render(request, 'signup.html', {
            'messages': ["Account verified successfully. You can now login."]
        })
    else:
        return render(request, 'signup.html', {
            'invalid': " Invalid or expired verification link."
        })
    
@csrf_exempt
def loginnpage(request):
    if request.method == 'POST':
        fnm = request.POST.get('fnm')
        pwd = request.POST.get('pwd')

        try:
            user_obj = User.objects.get(username=fnm)
        except User.DoesNotExist:
            return render(request, 'loginn.html', {
                'invalid': "Invalid Username or Password"
            })
        
        
        if not user_obj.is_active:
            return render(request, 'loginn.html', {
                'invalid': "Please verify your email before login"
            })

        userr = authenticate(request, username=fnm, password=pwd)
        if userr is not None:
            login(request, userr)
            return redirect('/')
    return render(request, 'loginn.html')

def forgetPassword(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = f"http://{request.get_host()}/newPasswordPage/{uid}/{token}/"

            send_mail(
                subject="Reset Your Password – Linkup Social Media",
                message=f"Hello {user.username},\n\nReset your password using the link below:\n{reset_link}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            html_message = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style=" margin:0; padding:0; background-color:#0f0f0f; font-family: Arial, sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0f0f0f;">
<tr>
<td align="center" style="padding:20px;">

    <!-- Container -->
    <table width="100%" cellpadding="0" cellspacing="0" style=" max-width:480px; background-color:#0f0f0f; color:#ffffff;">

        <!-- Title -->
        <tr>
            <td style="padding-bottom:20px;">
                <h2 style=" margin:0; color:#ffffff; font-size:22px; text-align:left;">
                    Linkup Social Media
                </h2>
            </td>
        </tr>

        <!-- Greeting -->
        <tr>
            <td style="padding-bottom:12px; color:#d1d5db; font-size:16px;">
                Hello <b>{user.username}</b>,
            </td>
        </tr>

        <!-- Message -->
        <tr>
            <td style="padding-bottom:20px; color:#d1d5db; font-size:16px; line-height:1.5;">
                We received a request to reset your password.
                Click the button below to proceed.
            </td>
        </tr>

        <!-- Card -->
        <tr>
            <td style=" background-color:#10a37f; padding:24px; border-radius:14px; text-align:center;">
                <a href="{reset_link}" style=" display:inline-block; padding:14px 28px; background-color:#2563eb; color:#ffffff; text-decoration:none; border-radius:10px; font-size:16px; font-weight:bold;">
                    Reset Password
                </a>
            </td>
        </tr>

        <!-- Info -->
        <tr>
            <td style=" padding-top:20px; font-size:14px; color:#9ca3af; line-height:1.4;">
                If you did not request a password reset, please ignore this email.
                Your account will remain secure.
            </td>
        </tr>

        <!-- Footer -->
        <tr>
            <td style=" padding-top:24px; font-size:14px; color:#9ca3af;
            ">
                Regards,<br>
                <b>Linkup Social Media Support Team</b>
            </td>
        </tr>

    </table>

</td>
</tr>
</table>

</body>
</html>
"""

        )

            return render(request, 'forget_password.html', {
                'messages': ["Password reset link has been sent to your email."]
            })

        return render(request, 'forget_password.html', {
            'invalid': "Email not registered."
        })

    return render(request, 'forget_password.html')

def newPasswordPage(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return HttpResponse("Invalid or expired reset link")

    if request.method == "POST":
        pass1 = request.POST.get("Password1")
        pass2 = request.POST.get("Password2")

        if pass1 != pass2:
            return render(request, 'new_password.html', {
                'invalid': "Passwords do not match"
            })
        user.set_password(pass1)
        user.save()
        return render(request, 'loginn.html', {
            'messages': ["Password reset successful. You can now login."]
        })
    return render(request, 'new_password.html')

def logoutpage(request):
    logout(request)
    return redirect('loginn')

def uploadpage(request):
    if request.method == 'POST':
        user = request.user.username
        caption = request.POST.get('caption')

        image = request.FILES.get('image_upload')
        video = request.FILES.get('video')

        new_post = Post.objects.create(
            user=user,
            caption=caption,
            image=image if image else None,
            video=video if video else None
        )

        new_post.save()
        return redirect('/')

    return redirect('/')

@login_required(login_url='loginn')
def home(request):
    following_users = Followers.objects.filter(follower=request.user.username).values_list('user', flat=True)
    post = Post.objects.filter(Q(user=request.user.username) | Q(user__in=following_users)).order_by('-created_at')
    profile = Profile.objects.get(user=request.user)

    context = {
        'post': post,
        'profile': profile,
    }
    return render(request, 'main.html',context)

def likepage(request, id):
    if request.method == "GET":
        username = request.user.username
        post = get_object_or_404(Post, id=id)
        like_filter = Likepost.objects.filter(post=post, username=username).first()
        if like_filter is None:
            Likepost.objects.create(post=post, username=username)
            post.no_of_likes += 1
        else:
            like_filter.delete()
            post.no_of_likes -= 1  

        post.save()
        return redirect('/#' + str(id))

def home_post(request):
    post=Post.objects.get(id=id)
    profile=Profile.object.get(user=request.user)
    context ={
        'post':post,
        'profile':profile
    }
    return render(request,'main.html',context)
@login_required(login_url='loginn')
def explorepage(request):
    post=Post.objects.all().order_by('-created_at')
    profile=Profile.objects.get(user=request.user)
    context={ 
        'post':post,
        "profile":profile
    }
    return render(request,'explore.html',context)
@login_required(login_url='loginn')
def profilepage(request, id_user):
    user_object = get_object_or_404(User, username=id_user)
    profile, _ = Profile.objects.get_or_create(user=request.user)
    user_profile, _ = Profile.objects.get_or_create(user=user_object)
    user_posts = Post.objects.filter(user=id_user).order_by('-created_at')
    user_post_length = user_posts.count()
    follower = request.user.username
    user = id_user
    if Followers.objects.filter(follower=follower, user=user).exists():
        follow_unfollow = 'Unfollow'
    else:
        follow_unfollow = 'Follow'

    user_followers = Followers.objects.filter(user=id_user).count()
    user_following = Followers.objects.filter(follower=id_user).count()

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'profile': profile,
        'follow_unfollow': follow_unfollow,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    
    if request.user.username == id_user:
        if request.method == 'POST':
            bio = request.POST.get('bio', '')
            location = request.POST.get('location', '')
            image = request.FILES.get('image', user_profile.profileimg)

            user_profile.bio = bio
            user_profile.location = location
            user_profile.profileimg = image
            user_profile.save()

            return redirect(f'/profile/{id_user}')
    
    return render(request, 'profile.html', context)
@login_required(login_url='loginn')
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
def followpage(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if Followers.objects.filter(follower=follower, user=user).first():
            delete_follower = Followers.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = Followers.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')
@login_required(login_url='loginn')
def followpage(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if Followers.objects.filter(follower=follower, user=user).first():
            delete_follower = Followers.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = Followers.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')
@login_required(login_url='loginn')
def deletepage(request,id):
    post=Post.objects.get(id=id)
    post.delete()
    return redirect('/profile/'+request.user.username)
@login_required(login_url='loginn')
def search_results(request):
    query = request.GET.get('q')
    users = Profile.objects.filter(user__username__icontains=query)
    posts = Post.objects.filter(caption__icontains=query)
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    context = {
        'query': query,
        'users': users,
        'posts': posts,
        'profile' :profile,
    }
    
    return render(request, 'search_user.html', context)
@login_required(login_url='loginn')
def account(request):
    users = Profile.objects.select_related('user').all()
    profile, _ = Profile.objects.get_or_create(user=request.user)

    context = {
        'users': users,
        'profile': profile,
    }
    return render(request, 'account.html', context)

@login_required(login_url='loginn')
def reels(request):
    reels = Post.objects.filter(video__isnull=False).order_by('-id')
    return render(request, 'reels.html', {'reels': reels})
@login_required(login_url='loginn')
@csrf_exempt
def add_comment(request):
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        text = request.POST.get("text")
        user = request.user.username

        post = Post.objects.get(id=post_id)
        comment = Comment.objects.create(
            post=post,
            user=user,
            text=text
        )

        return JsonResponse({
            "user": comment.user,
            "text": comment.text
        })
@login_required(login_url='loginn') 
def searched(request):
    query = request.GET.get('query')
    users = User.objects.filter(username__icontains=query)
    profile, _ = Profile.objects.get_or_create(user=request.user)
    posts = Post.objects.filter(caption__icontains=query)
    context = {
        'users' :users,
        'profile': profile,
        'psots' :posts,
    }
    return render(request, "account.html",context)