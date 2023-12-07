from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from xml.etree import ElementTree as ET

from core.models import Player

from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse



YEAR = '2023'

file_path = '/app/core/api/token.json'

import os


def home(request):
    data = Player.objects.all().order_by("points_per_game")
    values = []
    for player in data:
        values.append(player.name)

    return HttpResponse(values)

def injuries(request):
    
    injured = Player.objects.filter((Q(status='INJ') | Q(status='O')) & Q(fan_pts__gte=28)).order_by("fan_pts")

    return HttpResponse(injured)

def benefitting(request):
    injured = Player.objects.filter((Q(status='INJ') | Q(status='O')) & Q(fan_pts__gte=28)).order_by("time_of_last_update", "-fan_pts")
    players_to_benefitting_players = {}
    players_to_time_of_injury = {}
    for player in injured:
        positions = player.positions.split(",")
        same_team_and_fantasy_points_query = Q(team=player.team) & Q(fan_pts__lt=26)

        overlapping_positions_query = Q()
        for position in positions:
            overlapping_positions_query |= Q(positions__contains=position)

        benefiting_players = Player.objects.filter(
            same_team_and_fantasy_points_query & overlapping_positions_query
        ).exclude(
            id=player.id
        ).values_list('name', flat=True).order_by("-fan_pts")[0:3]

        players_to_benefitting_players[player.name] = list(benefiting_players)
        players_to_time_of_injury[player.name] = player.time_of_last_update

    combined_data = {
        "benefitting_players": players_to_benefitting_players,
        "time_of_injury": players_to_time_of_injury
    }

    return JsonResponse(combined_data)

def login(request):
    return HttpResponse("LOGIN")
