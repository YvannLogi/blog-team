from django.contrib import admin
from django.db.models import Count

from .models import Category, Comment, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "post_count", "created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_post_count=Count("posts"))

    @admin.display(description="Posts", ordering="_post_count")
    def post_count(self, obj):
        return obj._post_count


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title", "author", "category_list",
        "is_verified", "published_status", "created_at",
    ]
    list_editable = ["is_verified"]
    list_filter = ["is_verified", "categories", "created_at"]
    search_fields = ["title", "content", "author__first_name", "author__phone"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
    list_per_page = 25

    filter_horizontal = ["categories"]
    readonly_fields = ["created_at", "updated_at"]
    list_select_related = ["author"]

    fieldsets = [
        (None, {"fields": ["title", "content", "categories"]}),
        ("Publication", {"fields": ["author", "is_verified"]}),
        ("Dates", {"fields": ["created_at", "updated_at"], "classes": ["collapse"]}),
    ]

    actions = ["mark_verified", "mark_unverified"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("categories")

    @admin.display(description="Categories")
    def category_list(self, obj):
        return ", ".join(c.name for c in obj.categories.all()) or "—"

    @admin.display(description="Published", boolean=True)
    def published_status(self, obj):
        return obj.is_published

    @admin.action(description="Mark selected posts as verified")
    def mark_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} post(s) verified.")

    @admin.action(description="Mark selected posts as not verified")
    def mark_unverified(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"{updated} post(s) unverified.")

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "post", "parent", "is_active", "created_at"]
    list_editable = ["is_active"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["content", "user__first_name", "user__phone", "post__title"]
    list_select_related = ["user", "post", "parent"]
    raw_id_fields = ["post", "parent"]
    readonly_fields = ["created_at", "updated_at", "edited_at"]

    fieldsets = [
        (None, {"fields": ["user", "post", "parent", "content"]}),
        ("Modération", {"fields": ["is_active"]}),
        ("Dates", {"fields": ["created_at", "updated_at", "edited_at"], "classes": ["collapse"]}),
    ]

    actions = ["activate", "deactivate"]

    def get_actions(self, request):
        # on retire la suppression en masse : on désactive au lieu de supprimer
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    @admin.action(description="Activer les commentaires sélectionnés")
    def activate(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} commentaire(s) activé(s).")

    @admin.action(description="Désactiver les commentaires sélectionnés")
    def deactivate(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} commentaire(s) désactivé(s).")
