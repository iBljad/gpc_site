from datetime import timedelta
from django.core.mail import send_mail, BadHeaderError
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login as auth_login
from django.contrib.auth.models import User, Permission
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.models import Avg, Count
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import GamesDD, SearchForm, UserVote, ContactForm
from .models import Req, Platform, Game, Link, GamesDDForm, RegisterForm, LoginForm, Votes


def index(request):
    form = ContactForm
    # reqs = Req.objects.filter(active=True).order_by('-pub_date')[:15]
    # platforms = Platform.objects.all()
    messages.debug(request, 'Test')

    return render(request, 'cts_app/index.html',
                  {''' 'platforms': platforms,  'reqs': reqs,''' 'nbar': 'home'})


def create(request):
    if request.method == 'POST':

        f = GamesDDForm(request.POST)
        GamesDDForm.full_clean(f)

        try:
            ttt = Req.objects.get(active=True, game=request.POST.get('game', ''),
                                  platform=request.POST.get('platform', ''),
                                  nickname=request.user,
                                  pub_date__gte=timezone.now() - timedelta(days=1))
            messages.warning(request, 'Request with the same platform, game and nickname already exists')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except Req.DoesNotExist:
            try:
                f.save()
            except ValidationError as e:
                return HttpResponse(e.message_dict)

            else:
                messages.success(request, 'Your request was successfully posted')
                return HttpResponseRedirect(reverse('cts_app:index'))
    else:
        try:
            platform_id = request.GET.get('platform_id', '')
            platform = Platform.objects.get(pk=platform_id)
            link = Link.objects.filter(platform=platform).values('game')
            games = Game.objects.filter(id__in=link)
            form = GamesDD(user=request.user, games=games, platform=platform)
        except Platform.DoesNotExist:
            raise Http404("Error occurred")
        return render(request, 'cts_app/create.html', {'games': games, 'forms': form, 'nbar': 'create'})


def search(request):
    search_type = request.GET.get('type', 'none')
    if search_type == 'search':
        if request.GET.get('game', '') != '' and request.GET.get('platform', '') != '' and request.GET.get('nickname',
                                                                                                           '').strip() != '':
            result = Req.objects.filter(active=True, game=request.GET.get('game', ''),
                                        platform=request.GET.get('platform', ''),
                                        nickname__username__iexact=request.GET.get('nickname', '').strip()).order_by(
                '-pub_date')

        elif request.GET.get('game', '') != '' and request.GET.get('platform', '') != '' and request.GET.get('nickname',
                                                                                                             '').strip() == '':
            result = Req.objects.filter(active=True, game=request.GET.get('game', ''),
                                        platform=request.GET.get('platform', '')).order_by('-pub_date')

        elif request.GET.get('game', '') != '' and request.GET.get('platform', '') == '' and request.GET.get('nickname',
                                                                                                             '').strip() != '':
            result = Req.objects.filter(active=True, game=request.GET.get('game', ''),
                                        nickname__username__iexact=request.GET.get('nickname', '').strip()).order_by(
                '-pub_date')

        elif request.GET.get('game', '') != '' and request.GET.get('platform', '') == '' and request.GET.get('nickname',
                                                                                                             '').strip() == '':
            result = Req.objects.filter(active=True, game=request.GET.get('game', '')).order_by('-pub_date')

        elif request.GET.get('game', '') == '' and request.GET.get('platform', '') != '' and request.GET.get('nickname',
                                                                                                             '').strip() != '':
            result = Req.objects.filter(active=True, platform=request.GET.get('platform', ''),
                                        nickname__username__iexact=request.GET.get('nickname', '').strip()).order_by(
                '-pub_date')

        elif request.GET.get('game', '') == '' and request.GET.get('platform', '') != '' and request.GET.get('nickname',
                                                                                                             '').strip() == '':
            result = Req.objects.filter(active=True, platform=request.GET.get('platform', '')).order_by('-pub_date')

        elif request.GET.get('game', '') == '' and request.GET.get('platform', '') == '' and request.GET.get('nickname',
                                                                                                             '').strip() != '':
            result = Req.objects.filter(active=True,
                                        nickname__username__iexact=request.GET.get('nickname', '').strip()).order_by(
                '-pub_date')
        else:
            messages.warning(request, 'Please select at least one field to search')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return render(request, 'cts_app/result.html', {'nbar': 'search', 'result': result})
    elif search_type == 'quicksearch':
        result = Req.objects.filter(
            Q(active=True, game__game__icontains=request.GET.get('query', '')) |
            Q(active=True, platform__platform__icontains=request.GET.get('query', '')) |
            Q(active=True, nickname__username__icontains=request.GET.get('query', '').strip()))
        return render(request, 'cts_app/result.html', {'nbar': 'search', 'result': result})
    else:
        form = SearchForm()
        return render(request, 'cts_app/search.html', {'forms': form, 'nbar': 'search'})


def login(request):
    next_page = request.GET.get('next', 'cts_app:index')
    if request.GET.get('action', '') == 'logout':
        if request.user.is_authenticated():
            logout(request)
            messages.success(request, 'You were successfully logged out')
            return redirect(request.GET.get('next', 'cts_app:index'))
        else:
            messages.warning('You are not logged in')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    elif request.POST.get('action', '') == 'login':
        login_form = LoginForm(request.POST)
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                messages.success(request, 'You were successfully logged in')
                # HttpResponseRedirect(redirect_to)
                return redirect(next_page)
            else:
                login_form.add_error('Your account was disabled')
                return render(request, 'cts_app/login.html',
                              {'nbar': 'Log in/register', 'forms': login_form, 'forms2': RegisterForm(),
                               'next': next_page})
                # TODO Return an 'invalid login' error message.
        else:
            login_form.add_error(field=None, error='Invalid login or password')
            return render(request, 'cts_app/login.html',
                          {'nbar': 'Log in/register', 'forms': login_form, 'forms2': RegisterForm(),
                           'next': next_page})
    elif request.POST.get('action', '') == 'register':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                ttt = User.objects.get(email=form.cleaned_data['email'])
                form.add_error('email', 'Email already exists')
                return render(request, 'cts_app/login.html',
                              {'nbar': 'Log in/register', 'forms': LoginForm(), 'forms2': form,
                               'next': next_page})
            except User.DoesNotExist:
                u = User.objects.create_user(username=form.cleaned_data['username'],
                                             email=form.cleaned_data['email'],
                                             password=form.cleaned_data['password'])
                p1 = Permission.objects.get(name__icontains='Can add req')
                p2 = Permission.objects.get(name__icontains='Can change req')
                p3 = Permission.objects.get(name__icontains='Can delete req')
                u.user_permissions.add(p1, p2, p3)

                username = request.POST.get('username', '')
                password = request.POST.get('password', '')
                user = authenticate(username=username, password=password)
                auth_login(request, user)
                messages.success(request, 'You were successfully registered, thanks!')
                return redirect(next_page)
        else:
            return render(request, 'cts_app/login.html',
                          {'nbar': 'Log in/register', 'forms': LoginForm(), 'forms2': form,
                           'next': next_page})
    else:
        return render(request, 'cts_app/login.html',
                      {'nbar': 'Log in/register', 'forms': LoginForm(), 'forms2': RegisterForm(),
                       'next': next_page})


def profile(request, user=''):
    if request.method == 'POST':
        try:
            user = User.objects.get(username=request.POST.get('user', ''))
            voted_user = User.objects.get(username=request.POST.get('voted_user', ''))
        except User.DoesNotExist:
            raise Http404("User doesn\'t exists")
        else:
            try:
                vote = Votes.objects.get(user=user, voted_user=voted_user)

            except Votes.DoesNotExist:
                Votes.objects.create(user=user, voted_user=voted_user, rate=request.POST.get('rate', ''),
                                     comment=request.POST.get('comment', ''))
            else:
                vote.rate = request.POST.get('rate', '')
                vote.comment = request.POST.get('comment', '')
                vote.pub_date = timezone.now()
                vote.save(update_fields=['rate', 'comment', 'pub_date'])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    try:
        user = User.objects.get(username=user)
    except User.DoesNotExist:
        raise Http404("User doesnt exists!")

    form = UserVote(user=user, voted_user=request.user)
    votes = Votes.objects.filter(user=user).order_by('-pub_date')

    platforms = Platform.objects.select_related('Req').filter(req__nickname=user).values('platform').annotate(
        count=Count('platform')).order_by('-count')

    games = Game.objects.select_related('Req').filter(req__nickname=user).values('game').annotate(
        count=Count('game')).order_by('-count')

    reqs = Req.objects.filter(active=True, nickname=user.id).order_by('-pub_date')[:15]

    rating = Votes.objects.filter(user=user).aggregate(Avg('rate'))['rate__avg']

    return render(request, 'cts_app/profile.html', {'nbar': 'profile', 'user1': user, 'forms': form, 'votes': votes,
                                                    'rating': rating, 'reqs': reqs, 'platforms': platforms,
                                                    'games': games})


def reqdel(request, req_id):
    if request.user.username == Req.objects.get(id=req_id).nickname.__str__() and request.user.is_authenticated():
        Req.objects.filter(id=req_id).update(active=False)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def top(request, entity):
    if entity == 'platform':
        result = Platform.objects.select_related('Req').filter(req__nickname__gte=0).values('platform').annotate(
            count=Count('platform')).order_by('-count')[:10]

    elif entity == 'game':
        result = Game.objects.select_related('Req').filter(req__nickname__gte=0).values('game').annotate(
            count=Count('game')).order_by('-count')[:10]
    elif entity == 'user':
        result = User.objects.select_related('Req').filter(req__nickname__gte=0).values('username').annotate(
            count=Count('username')).order_by('-count')[:10]
    return render(request, 'cts_app/tops.html', {'nbar': 'tops', 'entity': entity, 'result': result})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        subject = request.POST.get('subject', '')
        if subject != '':
            subject = '[CTS] ' + subject
        else:
            subject = '[CTS] No subject'

        from_email = request.POST.get('email', '')

        if from_email != '':
            message = request.POST.get('email', '') + ': \n' + request.POST.get('message', '')
        else:
            message = request.POST.get('message', '')
        if request.POST.get('message', '') != '':
            try:
                send_mail(subject, message, 'goplaycoop@yandex.ru', ['drakonmail@gmail.com'], fail_silently=True)
            except BadHeaderError:
                messages.success(request, 'Invalid header found.')
                return HttpResponseRedirect(reverse('cts_app:contact'))
            messages.success(request, 'Your message was sent, thanks!')
            return HttpResponseRedirect(reverse('cts_app:index'))
        else:
            return render(request, 'cts_app/contact.html', {'nbar': 'contact', 'forms': form})

    form = ContactForm
    return render(request, 'cts_app/contact.html', {'nbar': 'contact', 'forms': form})