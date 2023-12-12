from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import Category


def send_email(subject, html_message, recipients):
    recipients = recipients
    if len(recipients) < 1:
        return
    html_message = html_message
    for k, v in recipients.items():
        html_message = f'<p><h3>Здравствуйте {k}!</h3></p>{html_message}'
        msg = EmailMultiAlternatives(
            subject=subject,
            body='',
            from_email=f'{settings.EMAIL_HOST_USER}@yandex.ru',
            to=[v]
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send()


def send_comment_notification(post, comment):
    full_path = f'{settings.SITE_URL}/posts/'
    subject = 'На портале "Доска объявлений" добавлен отклик на Ваше объявление.'
    html_message = (f'<br />Пользователь {comment.user.username} оставил отклик на Ваше объявление: <br />'
                    f'"{post.title}"<br /><br />')
    html_message += f'\n<a href="{full_path}{post.pk}">Перейти на страницу объявления</a>\n<br />'
    recipient = {post.user.username: post.user.email}
    send_email(subject, html_message, recipient)


def send_apply_comment_notification(post, comment):
    subject = f'На портале "Доска объявлений" принят Ваш отклик.'
    html_message = f'<br />Автор объявления <br /> {post.title} <br /> принял Ваш отклик! <br /><br />'
    html_message += f'<p>{comment.text}</p>'
    recipient = {comment.user.username: comment.user.email}
    send_email(subject, html_message, recipient)


def _get_recipients(categories):
    recipients = {}
    for cat in Category.objects.filter(pk__in=categories):
        for user in cat.subscribers.all():
            recipients[user.username] = user.email
    return recipients


def send_newsletters(posts, categories):
    full_path = f'{settings.SITE_URL}/posts/'
    subject = f'Рассылка новостей за неделю портала "Доска объявлений".'
    recipients = _get_recipients(categories)
    html_message = '<br />Вы получили это письмо так как подписаны на рассылку.<br /><br />'
    html_message += 'Новые объявления:'
    for post in posts:
        html_message += f'\n<br /><a href="{full_path}{post.pk}">{post.title}</a>'
    send_email(subject, html_message, recipients)
