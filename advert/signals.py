from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment, Post
from .utils import send_comment_notification, send_apply_comment_notification


@receiver(post_save, sender=Comment)
def notify_comment_save(sender, instance, created, **kwargs):
    post = Post.objects.get(pk=instance.post_id)
    if created:
        send_comment_notification(post, instance)
    elif kwargs['update_fields'] and 'status' in kwargs['update_fields']:
        if instance.status:
            send_apply_comment_notification(post, instance)
