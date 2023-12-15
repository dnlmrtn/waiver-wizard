from django.db import models
from django.utils import timezone

class Player(models.Model):
    PLAYER_STATUS_CHOICES = [
        ('gtd', 'GTD'),
        ('out', 'O'),
        ('injured', 'INJ'),
        ('healthy', 'H')
    ]
    yahoo_id = models.CharField(max_length=6)
    name = models.CharField(max_length=100)
    photo_url = models.CharField(max_length=500)
    team = models.CharField(max_length=50)
    positions = models.CharField(max_length=50)
    status = models.CharField(
        max_length=10, choices=PLAYER_STATUS_CHOICES, default='active')
    time_of_last_update = models.DateTimeField(auto_now=True)
    
    points_per_game = models.DecimalField(max_digits=5, decimal_places=2)
    assists_per_game = models.DecimalField(max_digits=5, decimal_places=2)
    rebounds_per_game = models.DecimalField(max_digits=5, decimal_places=2)
    steals_per_game = models.DecimalField(max_digits=5, decimal_places=2)
    blocks_per_game = models.DecimalField(max_digits=5, decimal_places=2)
    to_per_game = models.DecimalField(max_digits=5, decimal_places=2)

    fan_pts = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name

    # Modified save method. This ensures time_of_last_update be changed on 'status' update only.
    # We do not want time_of_last_update changing when the player stats are updated weekly. 
    def save(self, *args, **kwargs):
        if self.pk is not None:
            # Fetch the existing record from the database
            old_record = Player.objects.get(pk=self.pk)
            if old_record.status != self.status:
                # Update the time_of_last_update only if status has changed
                self.time_of_last_update = timezone.now()
        else:
            # This is a new record, so no need to update time_of_last_update
            pass

        super(Player, self).save(*args, **kwargs)

class Games(models.Model):
    date = models.DateTimeField()
    home_team = models.CharField(max_length=50)
    away_team = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} on {self.date}"

class PlayerInjuries(models.Model):
    page = models.CharField(max_length=50)
    data = models.JSONField()

