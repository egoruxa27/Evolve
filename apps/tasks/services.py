from django.utils import timezone


def complete_task(task, user):
    task.status = task.Status.COMPLETED
    task.completed_at = timezone.now()

    user.xp_amount += task.xp_reward

    if user.xp_amount >= 100:
        user.xp_amount -= 100
        user.level += 1
    
    task.save()
    user.save()
