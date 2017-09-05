from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm


class Platform(models.Model):
    platform = models.CharField(max_length=20)

    def __str__(self):
        return self.platform


class Game(models.Model):
    game = models.CharField(max_length=1000)
    genre = models.CharField(max_length=100)

    # release_date = models.DateField('release date', null=True)

    def __str__(self):
        return self.game


class Language(models.Model):
    language = models.CharField(max_length=100)


class Req(models.Model):
    platform = models.ForeignKey(Platform)
    game = models.ForeignKey(Game)
    nickname = models.ForeignKey(User)
    comment = models.CharField(max_length=280, blank=True)
    pub_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    language = models.ForeignKey(Language)
    mic = models.BooleanField()

    def __str__(self):
        return self.pub_date.__str__()


class Link(models.Model):
    class Meta:
        unique_together = ('game', 'platform')
    game = models.ForeignKey(Game)
    platform = models.ForeignKey(Platform)


class SearchFormModel(ModelForm):
    class Meta:
        model = Req
        exclude = ['pub_date', 'comment']


# class GamesDDForm(ModelForm):
#     game_1 = models.ForeignKey(Game)
#     platform = models.ForeignKey(Platform)
#     class Meta:
#         model = Req
#         fields = ['game_1', 'platform', 'nickname']


class RegisterForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        default_permissions = ()

    password = forms.CharField(widget=forms.PasswordInput)


class LoginForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = User
        fields = ['username', 'password']

    password = forms.CharField(widget=forms.PasswordInput)


# class Gamer(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     rating = models.CharField(max_length=100)


class Votes(models.Model):
    user = models.ForeignKey(User)
    rate = models.PositiveSmallIntegerField()
    comment = models.CharField(max_length=1000, blank=True)
    voted_user = models.ForeignKey(User, related_name='Voter')
    pub_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("user", "voted_user"),)
