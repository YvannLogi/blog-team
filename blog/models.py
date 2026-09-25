from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.mixins import TimeMixin
from .queryset import PostQueryset
from django.utils.text import slugify


class Category(TimeMixin):
    name = models.CharField("Category Name", max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(TimeMixin):
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        blank=True, null=True, related_name="posts"
    )

    categories = models.ManyToManyField(Category, related_name="posts")

    title = models.CharField("Title of your post", max_length=200, db_index=True)
    content = models.TextField("Describe the post", blank=True, null=True)
    guest_name = models.CharField("Your first name", max_length=100, blank=True)

    is_verified = models.BooleanField(default=True)

    objects = PostQueryset.as_manager()

    def get_absolute_url(self):
        from django.urls import reverse
        category = self.categories.first()

        return reverse('blog:post-detail', kwargs={
            'date': self.created_at.strftime('%Y-%m-%d'),
            'cat': category.slug if category else "no-slug-or-classe",
            'pk': self.pk
        })

    @property
    def author_name(self):
        if self.author:
            return self.author.first_name
        return self.guest_name or "Anonymous"

    def __str__(self):
        return f"{self.title} by {self.author_name}"


    @property
    def is_published(self):
        return (
            self.is_verified and
            self.created_at is not None and
            self.created_at <= timezone.now()
        )

    # class Meta:
    #     ordering = ['-created_at']


""" write a comment """
class Comment(TimeMixin):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="comments",
    )

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    # Si parent est vide -> commentaire principal ; sinon -> réponse à ce parent
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        blank=True, null=True
    )

    content = models.TextField("Your comment")

    is_active = models.BooleanField("Active", default=True, db_index=True)

    # Rempli seulement quand l'auteur modifie son texte (pas par l'admin)
    edited_at = models.DateTimeField("Edited at", blank=True, null=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        author = self.user.first_name if self.user else "None user"

        return f'Comment by {author} on post : {self.post.title}'
