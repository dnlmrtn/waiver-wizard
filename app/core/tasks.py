from celery import shared_task
from celery.signals import worker_ready

from core.usecases import UpdatePlayerDataUseCase 


@shared_task
def update_player_stats():
    UpdatePlayerDataUseCase().update_player_stats()

@shared_task
def update_player_status():
    # Update status data
    UpdatePlayerDataUseCase().update_player_status()


@worker_ready.connect
def at_start(sender, **kwargs):
    with sender.app.connection() as conn:
        sender.app.send_task('core.tasks.update_player_stats')

        sender.app.send_task('core.tasks.update_player_status')
