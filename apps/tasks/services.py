from django.utils import timezone


def complete_task(task, user):
    if task.status in (
        task.Status.COMPLETED,
        task.Status.FAILED,
    ):
        return
    
    completed_at = timezone.now()

    if task.deadline < completed_at:
        task.status = task.Status.FAILED
    else:
        task.status = task.Status.COMPLETED
        user.xp_amount += task.xp_reward

    task.completed_at = completed_at

    if user.xp_amount >= 100:
        user.xp_amount -= 100
        user.level += 1
    
    task.save()
    user.save()
