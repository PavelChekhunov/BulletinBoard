from celery import shared_task
import datetime
from .models import Post
from .utils import send_newsletters


@shared_task
def newsletters():
    today = datetime.datetime.now()
    days_ago = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(datetime_created__gte=days_ago)
    if posts and len(posts) > 0:
        categories_id = set(posts.values_list('category__pk', flat=True))
        send_newsletters(posts, categories_id)
