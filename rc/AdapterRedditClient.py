import random
import string
from datetime import datetime

from praw import Reddit

from .models import Token, Post, State
from .secret import *


class AdapterRedditClient:
    @staticmethod
    def _readonly_client():
        return Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=UA)

    def __init__(self, user='', interest=None):
        tokens_by_user = Token.objects.filter(user__exact=user)
        token_by_user_and_interest = tokens_by_user.filter(interest__exact=interest)

        try:
            self.a = token_by_user_and_interest.get()
            self.reddit = Reddit(client_id=CLIENT_ID,
                                 client_secret=CLIENT_SECRET,
                                 refresh_token=self.a.token,
                                 user_agent=UA)

        except Token.DoesNotExist:
            self.a = 'ReadOnly'
            self.reddit = self._readonly_client()

    @staticmethod
    def first_time_user(context, interest):
        while True:
            state = AdapterRedditClient.gen_state()
            if not State.objects.filter(state__exact=state).exists():
                a = State.objects.create(interest=interest, state=state, user=context.author.id)
                r = Reddit(client_id=CLIENT_ID,
                           client_secret=CLIENT_SECRET,
                           redirect_uri='https://redcord.ks-dev.com/auth',
                           user_agent=UA)
                return r.auth.url(['submit', 'edit', 'read'], a.state, 'permanent')

    @staticmethod
    def gen_state():
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
        return ''.join(random.choice(letters) for i in range(40))

    @staticmethod
    def refresh_token(code):
        r = AdapterRedditClient._readonly_client()
        return r.auth.authorize(code=code)

    def save_posts(self, watch_text):
        for submission in self.reddit.subreddit(watch_text).stream.submissions():
            p = Post.objects.create(post_id=submission.id,
                                    author=submission.author,
                                    title=submission.title,
                                    link=submission.shortlink,
                                    interest=submission.subreddit.id,
                                    date_added=datetime.fromtimestamp(submission.created_utc))

    def get_post(self, sub_id):
        return self.reddit.submission(id=sub_id).selftext

    def send_post(self, post_text, msg):
        if self.reddit.readonly:
            self.reddit.authorize()  # may fail, royally if a token is expired or does not exist
        self.reddit.post(path=post_text, data=msg)

# EOF
