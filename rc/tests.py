from django.test import TestCase
from datetime import datetime

from praw import Reddit
from rc.AdapterRedditClient import AdapterRedditClient
from rc.secret import CLIENT_ID, CLIENT_SECRET, UA
from rc.models import Setting, Post, Token


# Create your tests here.


class ModelsTest(TestCase):
    @staticmethod
    def create_setting(value=''):
        return Setting.objects.create(key='This', value=value)

    @staticmethod
    def create_post():
        return Post.objects.create(post_id='agi5zf', author='kmiller0112', title='test',
                                   link='https://www.reddit.com/r/test/comments/agi5zf/test/',
                                   date_added=datetime.utcfromtimestamp(1547647071))

    @staticmethod
    def reddit_client():
        return Reddit(client_id=CLIENT_ID,
                      client_secret=CLIENT_SECRET,
                      user_agent=UA)

    def test_Setting(self):
        s = self.create_setting(value='is not a test.')
        self.assertTrue(isinstance(s, Setting))
        self.assertEqual(s.__str__(), 'This:  is not a test.')

    def test_empty_Setting(self):
        s = self.create_setting()
        self.assertTrue(isinstance(s, Setting))
        self.assertEqual(s.__str__(), 'This:  NONE')

    def test_Post_body(self):
        p = self.create_post()
        self.assertTrue(isinstance(p, Post))
        r = self.reddit_client()
        self.assertEqual(p.post_body(client=r), 'test')

    def test_str_Post(self):
        p = self.create_post()
        self.assertTrue(isinstance(p, Post))
        self.assertEqual(p.__str__(), '[test](https://www.reddit.com/r/test/comments/agi5zf/test/)\nkmiller0112\n\n')


class RedditTest(TestCase):
    @staticmethod
    def refresh_token():
        return '164226473380-AaLP6xh86eWhH_wqpJ_nrTI6BPo'

    @staticmethod
    def authorized():
        return Token.objects.create(user='test', token=RedditTest.refresh_token())

    def test_reddit_readonly(self):
        r = AdapterRedditClient()
        self.assertTrue(isinstance(r, AdapterRedditClient))
        self.assertEqual(r.a, 'ReadOnly')

    def test_reddit_auth_known(self):
        self.authorized()
        r = AdapterRedditClient(user='test')
        self.assertTrue(isinstance(r, AdapterRedditClient))
        self.assertEqual(r.a.token, self.refresh_token())

    def test_reddit_auth_unknown(self):
        r = AdapterRedditClient(user='unknown')
        self.assertTrue(isinstance(r, AdapterRedditClient))
        self.assertEqual(r.a, 'ReadOnly')

    def test_gen_state(self):
        state = AdapterRedditClient.gen_state()
        self.assertTrue(len(state) == 40)




# EOF
