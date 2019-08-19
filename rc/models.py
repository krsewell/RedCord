from django.db import models
from discord.embeds import Embed
import datetime


# Create your models here.
class BaseModel(models.Model):
    class Meta:
        abstract = True
        app_label = 'rc'


class Setting(BaseModel):
    key = models.CharField(max_length=30, unique=True)
    value = models.CharField(max_length=90)

    def __str__(self):
        v = self.value if self.value else 'NONE'
        return '{}:  {}'.format(self.key, v)


class Post(BaseModel):
    post_id = models.CharField(primary_key=True, max_length=20, editable=False)
    author = models.CharField(max_length=30)
    title = models.CharField(max_length=90)
    link = models.URLField()
    date_added = models.DateTimeField()
    interest = models.CharField(max_length=15)

    def post_body(self, client):
        s = client.submission(id=self.post_id)
        return s.selftext

    def __str__(self):
        return '[{0}]({1})\n{2}\n\n'.format(self.title, self.link, self.author)


class Interest(BaseModel):
    WATCH = 'W'
    POST = 'P'
    REDDIT = 'R'
    DISCORD = 'D'
    SCOPE = [
        (WATCH, 'watch'),
        (POST, 'poster')
    ]
    SERVICE = [
        (REDDIT, 'reddit'),
        (DISCORD, 'discord')
    ]

    scope = models.CharField(max_length=1, choices=SCOPE, default=WATCH)
    service = models.CharField(max_length=1, choices=SERVICE, default=REDDIT)
    finder = models.CharField(max_length=90)
    pitch = models.CharField(max_length=50)
    next_task_run = models.DateTimeField(default=datetime.datetime.utcnow() + datetime.timedelta(0, 3600))

    def __str__(self):
        return '{} {} on {}.'.format(self.service, self.scope, self.finder)


class Pitch(BaseModel):
    name = models.CharField(max_length=50)
    part = models.CharField(max_length=30)
    body = models.TextField(max_length=1000)

    def __str__(self):
        pass


class Token(BaseModel):
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE, null=True)
    user = models.CharField(max_length=50)
    token = models.CharField(max_length=40, default='')
    created = models.DateTimeField(auto_now_add=True)


class State(BaseModel):
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    state = models.CharField(max_length=40, unique=True)
    user = models.CharField(max_length=50)


# EOF
