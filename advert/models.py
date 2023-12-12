from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=255, unique=True, null=True, default=None)
    subscribers = models.ManyToManyField(User, through='Subscribe')

    def __str__(self):
        return f'{self.name}'


class Post(models.Model):
    objects = models.Manager()
    title = models.CharField(max_length=120)
    text = models.TextField(default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime_created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.pk)])

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        self.text = self.text.replace('sandbox=""', '')
        super().save()


class Comment(models.Model):
    objects = models.Manager()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(default='')
    datetime_created = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)


class Subscribe(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
