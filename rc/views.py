from django.shortcuts import render
from django.http import Http404

from rc.models import State, Token
from rc.AdapterRedditClient import AdapterRedditClient


# Create your views here


def index(request):
    return render(request, 'rc/index.html')


def auth(request):
    # is there variables state and code?
    if request.method == 'GET':
        data = {
            'state': request.GET['state'],
            'code': request.GET['code']
        }
        if State.objects.filter(state__exact=data['state']).exist():
            state = State.objects.get(state__exact=data['state'])
            token = AdapterRedditClient.refresh_token(data['code'])
            Token.objects.create(interest=state.interest, user=state.user, token=token)
            state.delete()
            return render(request, 'rc/auth.html', data)
        else:
            raise Http404('Response not recognized. Please try your command again.')


# EOF
