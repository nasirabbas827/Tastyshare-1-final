from django.contrib import admin
from .models import CustomerUser, Recipe, Comment, Favorite

@admin.register(CustomerUser)
class CustomerUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'full_name', 'status', 'last_login', 'created_at')
    list_filter = ('status', 'gender', 'country')
    search_fields = ('username', 'email', 'full_name', 'phone')
    ordering = ('-created_at',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'cooking_time', 'status', 'created_at')
    list_filter = ('category', 'status')
    search_fields = ('title', 'description', 'ingredients', 'steps', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('user',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'rating', 'status', 'created_at')
    list_filter = ('status', 'rating')
    search_fields = ('user__username', 'recipe__title', 'text')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    autocomplete_fields = ('user', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created_at')
    search_fields = ('user__username', 'recipe__title')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    autocomplete_fields = ('user', 'recipe')
