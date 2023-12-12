from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Comment, Category, Subscribe
from .forms import AdvertForm
from django.contrib.auth.decorators import login_required


class PostsList(ListView):
    model = Post
    ordering = '-datetime_created'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user

        if current_user.is_authenticated:
            context['comments'] = (Comment.objects.filter(user=current_user, post=context['post'].pk)
                                   .order_by('-id')[:3].values())
            context['is_current_author'] = current_user == self.object.user
        return context


class PostCreate(LoginRequiredMixin, CreateView):
    form_class = AdvertForm
    model = Post
    template_name = 'post_edit.html'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        context['is_current_author'] = current_user.is_authenticated
        return context

    def form_valid(self, form):
        post = form.save(commit=False)
        post.user = self.request.user
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        retval = super().post(request, *args, **kwargs)
        # send_email_notification(request, self.object)
        # if _is_celery_working():
        #     newsletter.apply_async([self.object.id], countdown=3, expires=15)
        return retval


class PostUpdate(LoginRequiredMixin, UpdateView):
    form_class = AdvertForm
    model = Post
    template_name = 'post_edit.html'
    pk_url_kwarg = 'id'

    # permission_required = ('news.change_post', 'news.view_post')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        if current_user.is_authenticated:
            context['is_current_author'] = current_user == self.object.user
        return context


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')
    pk_url_kwarg = 'id'

    # permission_required = ('news.delete_post', 'news.view_post')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        if current_user.is_authenticated:
            context['is_current_author'] = current_user == self.object.user
        return context

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return HttpResponseRedirect(self.success_url)
        else:
            return super(PostDelete, self).post(request, *args, **kwargs)


class Comments(LoginRequiredMixin, ListView):
    model = Comment
    context_object_name = 'comments'
    template_name = 'comments.html'
    pk_url_kwarg = 'id'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.posts = None
        self.comments = None
        self.posts_filtered = []
        self.cmt_status = -1

    def get_queryset(self):
        self.posts = Post.objects.filter(user=self.request.user).order_by('-id')
        qset = super().get_queryset()
        self.comments = qset.filter(post__in=self.posts).order_by('-id')
        return self.comments

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = self.posts
        self.posts_filtered = self.request.session.get('posts_filtered', [])
        self.cmt_status = self.request.session.get('cmt_status', -1)
        self.comments = self._set_filter()
        context["posts_filtered"] = self.posts_filtered
        context["cmt_status"] = self.cmt_status
        context["comments"] = self.comments
        return context

    def post(self, request):
        if request.method == "POST":
            self.comments = self.get_queryset()
            if request.POST.get('btnRemoveFilter'):
                self.posts_filtered = []
                self.cmt_status = -1
            else:
                cmts = list(map(int, request.POST.getlist('cmt_comments')))
                if request.POST.get('btnApply'):
                    data = Comment.objects.filter(pk__in=cmts)
                    # data.update(status=1)
                    for item in data:
                        if item.status == 0:
                            item.status = 1
                            item.save(update_fields=['status'])
                elif request.POST.get('btnDelete'):
                    Comment.objects.filter(pk__in=cmts, status=0).delete()
                elif request.POST.get('btnRemove'):
                    Comment.objects.filter(pk__in=cmts, status=1).update(status=0)
                self.posts_filtered = list(map(int, request.POST.getlist('cmt_posts')))
                self.cmt_status = int(request.POST["cmt_type"])
                self.comments = self._set_filter()
            request.session["posts_filtered"] = self.posts_filtered
            request.session["cmt_status"] = self.cmt_status
        return HttpResponseRedirect('.')

    def _set_filter(self):
        if -1 < self.cmt_status < 2:
            self.comments = self.comments.filter(status=self.cmt_status == 1)
        if len(self.posts_filtered) > 0:
            self.comments = self.comments.filter(post__in=self.posts_filtered)
        return self.comments.order_by('-id')


def add_comment(request, **kwargs):
    if request.method == "POST" and request.user.is_authenticated:
        if request.POST["text_comment"].strip():
            post = Post.objects.get(pk=kwargs["id"])
            Comment.objects.create(post=post, user=request.user, text=request.POST["text_comment"])
    return redirect(f'/posts/{kwargs["id"]}')


def del_comment(request, **kwargs):
    Comment.objects.get(pk=kwargs["cid"]).delete()
    return redirect(f'/posts/{kwargs["id"]}')


class SubscribeCategory(LoginRequiredMixin, ListView):
    model = Category
    ordering = 'name'
    template_name = 'subscribe.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_anonymous:
            context['cat_subscribed'] = Subscribe.objects.filter(user=self.request.user).values_list('category',
                                                                                                     flat=True)
        return context


@login_required
def subscription(request):
    if not request.user.is_anonymous:
        Subscribe.objects.filter(user=request.user).delete()
        for item in request.POST.getlist('sc_cat'):
            cat = Category.objects.get(pk=item)
            cat.subscribers.add(request.user)
    # return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect('post_list')
