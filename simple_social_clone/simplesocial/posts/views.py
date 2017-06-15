from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.http import Http404
from django.views import generic

from braces.views import SelectRelatedMixin

from . import forms
from . import models

from django.contrib.auth import get_user_model
User = get_user_model() #someone logged in session, I am able to use user object as a current user call things after that
print(User)
print("aaaa")

class PostList(SelectRelatedMixin, generic.ListView):
    model = models.Post
    select_related = ("user", "group")
    #Mixin allows you to provide a tuple or list of related models to perform a select_related on


class UserPosts(generic.ListView):
    model = models.Post
    template_name = "posts/user_post_list.html"

    def get_queryset(self):
        try:
            self.post_user = User.objects.prefetch_related("posts").get(
                username__iexact=self.kwargs.get("username")
            )
            #print(User) #<class 'django.contrib.auth.models.User'>
            print((User.objects)
            # print(User.objects.prefetch_related("posts")) <QuerySet [<User: Dai>, <User: hana>, <User: kikuchi>, <User: dai>, <User: linh>, <User: test>, <User: hana1010>]>

        except User.DoesNotExist:
            raise Http404
        else:
            # print(self.post_user) hana1010
            # print(self.post_user.posts.all()) <QuerySet [<Post: test3>, <Post: Post2>, <Post: test>]>
            return self.post_user.posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_user"] = self.post_user
        return context


class PostDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Post
    select_related = ("user", "group")

    def get_queryset(self):
        queryset = super().get_queryset()
        print(queryset)
        # <QuerySet [<Post: dai>, <Post: Hana>, <Post: Third try>, <Post: This is my First post>]>
        return queryset.filter(
            user__username__iexact=self.kwargs.get("username")
        )

class CreatePost(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    # form_class = forms.PostForm
    fields = ('message','group')
    model = models.Post

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs.update({"user": self.request.user})
    #     return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class DeletePost(LoginRequiredMixin, SelectRelatedMixin, generic.DeleteView):
    model = models.Post
    select_related = ("user", "group")
    success_url = reverse_lazy("posts:all")

    def get_queryset(self):
        queryset = super().get_queryset()
        # print(queryset)  [<Post: test3>, <Post: Post2>, <Post: test>
        return queryset.filter(user_id=self.request.user.id)

    def delete(self, *args, **kwargs):
        # print(args) (<WSGIRequest: POST '/posts/delete/1/'>,)
        # print(kwargs){'pk': '1'}
        messages.success(self.request, "Post Deleted!")
        return super().delete(*args, **kwargs)
