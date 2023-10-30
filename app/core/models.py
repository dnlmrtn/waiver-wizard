from django.db import models


class Players(models.Model):
    PLAYER_STATUS_CHOICES = [
        ('active', 'A'),
        ('out', 'O'),
        ('injured', 'INJ')
    ]
    yahoo_id = models.CharField(max_length=6)
    name = models.CharField(max_length=100)
    team = models.CharField(max_length=50)
    positions = models.CharField(max_length=50)
    status = models.CharField(
        max_length=10, choices=PLAYER_STATUS_CHOICES, default='active')
    percent_owned = models.DecimalField(max_digits=5, decimal_places=2)

    minutes_per_game = models.DecimalField(max_digits=5, decimal_places=2)

    points_per_game = models.DecimalField(max_digits=5, decimal_places=2)
    assists_per_game = models.DecimalField(max_digits=5, decimal_places=2)
    rebounds_per_game = models.DecimalField(max_digits=5, decimal_places=2)
    steals_per_game = models.DecimalField(max_digits=5, decimal_places=2)
    blocks_per_game = models.DecimalField(max_digits=5, decimal_places=2)
    threes_per_game = models.DecimalField(max_digits=5, decimal_places=2)
    fg = models.DecimalField(max_digits=5, decimal_places=2)
    ft = models.DecimalField(max_digits=5, decimal_places=2)
    #to_per_game = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


class Games(models.Model):
    date = models.DateTimeField()
    home_team = models.CharField(max_length=50)
    away_team = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} on {self.date}"
