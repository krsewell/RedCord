import os
import sys

from discord.ext import commands
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.wsgi import get_wsgi_application

from rc.AdapterRedditClient import AdapterRedditClient
from rc.models import *
from rc.secret import DISCORD_TOKEN

description = 'REDcord is a bot, that automates reddit and/or discord recruiting and posting, provides guild ' \
              'reporting functions, and user management though discord commands.' \
              '\n\n' \
              'created by /u/redballons99 for The Bacon Family'

proj_path = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
os.environ.setdefault("DJANGO_SETTING_MODULE", "redcord.settings")
sys.path.append(proj_path)

os.chdir(proj_path)
application = get_wsgi_application()

bot = commands.Bot(command_prefix='?', description=description, case_insensitive=True)


def lower(arg):
    return arg.lower()


def format_post(param: Post):
    r = AdapterRedditClient()
    return '{}{}{}'.format(param.author, param.title, param.link) + r.get_post(param.id)


def check_finder(msg: lower):
    return msg[2:] if msg[:2] == 'r/' else msg


@bot.event()
async def on_ready():
    print('Logged in as: ' + bot.user.name + ' ' + bot.user.id)


@bot.group(description='Way to access and search recruitment posts', case_insensitive=True)
async def recruit(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Usage: "?recruit search <post title / id>"\n'
                       '       "?recruit watch <subreddit>"\n'
                       '       "?recruit unwatch <subreddit>"\n'
                       '       "?recruit post <pitch_name> <subreddit>"\n'
                       '       "?recruit unpost <pitch_name> <subreddit>"\n\n'
                       )


@recruit.command(name='search')
async def _search(ctx, *, msg: str, r: str = None):
    if Post.objects.filter(post_id__exact=msg).exists():
        p = format_post(Post.objects.get(post_id=msg))
        await ctx.send(p)
    else:
        for post in Post.objects.filter(title__icontains=msg):
            r += 'id:{} posted: {}\n'.format(post.post_id, post.author, post.title)
        await ctx.send(r)


@recruit.command(name='watch')
async def _watch(ctx, *, msg: str):
    msg = check_finder(msg)
    if Interest.objects.filter(scope='W').filter(finder__iexact=msg).exists():
        raise MultipleObjectsReturned()
    else:
        r = AdapterRedditClient()
        i = Interest.objects.create(scope='W', service='R', finder=msg)
        await ctx.send('Created ' + i)


@recruit.command(name='unwatch')
async def _unwatch(ctx, *, msg: str):
    msg = check_finder(msg)
    if Interest.objects.filter(scope='W').filter(finder__iexact=msg).exists():
        i = Interest.objects.get(finder__iexact=msg)
        output = i.__str__()
        i.delete()
        await ctx.send('Removed ' + output)
    else:
        raise ObjectDoesNotExist()


@recruit.command(name='post')
async def _post(ctx, pitch_name: lower, finder: lower):
    interest = Interest.objects.filter(scope='P')
    interest = interest.filter(user=ctx.author.id)
    existing_interest = interest.filter(finder_iexact=finder)

    if existing_interest.exists():  # the user has already created an interest
        raise MultipleObjectsReturned
    elif interest.exists():  # then we already have the users permission to post.
        new_interest = Interest.objects.create(scope='P', service='R', finder=finder, pitch=pitch_name)
        await ctx.send('Created {} for {}'.format(new_interest.__str__(), ctx.author.nick))
    else:
        new_interest = Interest.objects.create(scope='P', service='R', finder=finder, pitch=pitch_name)
        s1 = 'This operation requires a reddit account and user token to work properly. '
        s2 = 'Please follow [this link]({0})'.format(AdapterRedditClient.first_time_user(ctx, new_interest))
        s3 = ', sign in and authorize REDcord to post on your behalf for this request.'
        await ctx.send(
                'Created {} for {}\n\n{}{}{}'.format(new_interest.__str__(), ctx.author.nick, s1, s2, s3)
        )
    # this will require a user to successfully authenticate with oauth to create a token for our task to use.


@recruit.command(name='unpost')
async def _unpost(ctx, pitch_name: lower, finder: lower):
    interest = Interest.objects.filter(scope='P')
    interest = interest.filter(user__exact=ctx.author.id)
    interest = interest.filter(finder__iexact=finder)
    existing_interest = interest.filter(pitch__iexact=pitch_name)

    if existing_interest.exists():
        existing_interest.get().delete()


def is_key_update(msg):
    lst_msg = msg.split()
    if len(lst_msg) == 2:
        try:
            Setting.objects.get(key__iexact=lst_msg[0])
            return False if Setting.objects.filter(key__iexact=lst_msg[1]).exists() else True
        except Setting.DoesNotExist:
            return False
        except Setting.MultipleObjectsReturned:
            return False
    return False


@bot.command()
async def setting(ctx, *, msg: lower):
    if is_key_update(msg):
        d = msg.split()
        k = d[0] if d[0][:2] != 'k_' else d[0][2:]
        v = d[1]
        Setting.objects.create(key='k_{}'.format(k), value=v)

    elif msg is None:
        settings = Setting.objects.all()
        await ctx.send('\n'.join(settings))
    elif Setting.objects.filter(key__icontains=msg).exists():
        settings = Setting.objects.filter(key__icontains=msg)
        await ctx.send('\n'.join(settings))
    else:
        await ctx.send('No setting with %s found as its key.' % msg)


@bot.command()
async def pitch(ctx):
    pass


def start():
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)

# EOF
