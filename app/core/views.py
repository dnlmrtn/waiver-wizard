import os
from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from xml.etree import ElementTree as ET

from core.models import Player

from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse


YEAR = '2023'

file_path = '/app/core/api/token.json'


def home(request):
    data = Player.objects.all().order_by("points_per_game")
    values = []
    for player in data:
        values.append(player.name)

    return HttpResponse(values)


def injuries(request):

    injured = Player.objects.filter((Q(status='INJ') | Q(
        status='O')) & Q(fan_pts__gte=28)).order_by("fan_pts")

    return HttpResponse(injured)


def benefitting(request):
    injured = Player.objects.filter((Q(status='INJ') | Q(status='O')) & Q(
        fan_pts__gte=28)).order_by("time_of_last_update", "-fan_pts")

    injured_players = {}
    for player in injured:

        positions = player.positions.split(",")
        same_team_and_fantasy_points_query = Q(team=player.team) & Q(
            fan_pts__lt=player.fan_pts) & Q(fan_pts__lt=35) & Q(status='H')

        overlapping_positions_query = Q()
        for position in positions:
            overlapping_positions_query |= Q(positions__contains=position)

        benefiting_players = Player.objects.filter(
            same_team_and_fantasy_points_query & overlapping_positions_query
        ).exclude(
            id=player.id
        ).order_by("-fan_pts")[0:7]

        benefiting_players_with_stats = {benefitting_player.name: [benefitting_player.points_per_game, benefitting_player.rebounds_per_game, benefitting_player.assists_per_game,
                                                                   benefitting_player.steals_per_game, benefitting_player.blocks_per_game, benefitting_player.to_per_game] for benefitting_player in benefiting_players}

        injured_players[player.name] = {'photo_url': player.photo_url,
                                        'stats': [player.points_per_game, player.rebounds_per_game, player.assists_per_game,
                                                  player.steals_per_game, player.blocks_per_game, player.to_per_game],
                                        'benefiting_players': benefiting_players_with_stats,
                                        'time_of_injury': player.time_of_last_update,
                                        'status': player.status, }

    return JsonResponse(injured_players)


def login(request):
    return HttpResponse("LOGIN")
