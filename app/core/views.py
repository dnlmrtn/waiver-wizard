import os
from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from xml.etree import ElementTree as ET

from core.models import Player, Endpoint

from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse

import json


YEAR = '2023'

file_path = '/app/core/api/token.json'


def injuries(request):

    injured = Player.objects.filter((Q(status='INJ') | Q(
        status='O')) & Q(fan_pts__gte=28)).order_by("fan_pts")

    return HttpResponse(injured)


def benefitting(request):
    data = Endpoint.objects.filter(page='players')[0].data
    return JsonResponse(json.loads(data))


def login(request):
    return HttpResponse("LOGIN")
