from django.urls import path
from .views import (PostsList, PostDetail, PostCreate, PostUpdate, PostDelete, Comments,
                    add_comment, del_comment, SubscribeCategory, subscription)


urlpatterns = [
   path('', PostsList.as_view(), name="post_list"),
   path('<int:id>', PostDetail.as_view(), name="post_detail"),
   path('create/', PostCreate.as_view(), name='post_create'),
   path('<int:id>/edit/', PostUpdate.as_view(), name='post_update'),
   path('<int:id>/delete/', PostDelete.as_view(), name='post_delete'),
   path('<int:id>/add_comment/', add_comment, name='add_comment'),
   path('<int:id>/del_comment/<int:cid>', del_comment, name='del_comment'),
   path('comments/', Comments.as_view(), name='comments'),
   path('subscribe/', SubscribeCategory.as_view(), name="subscribe"),
   path('subscription/', subscription, name="subscription"),
]
