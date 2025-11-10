from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/delete/', views.delete_account, name='delete_account'),

    # Recipe CRUD
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipes/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('recipes/add/', views.recipe_create, name='recipe_create'),
    path('recipes/<int:pk>/edit/', views.recipe_update, name='recipe_update'),
    path('recipes/<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
    # Favorites
    path('recipes/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('about/', views.about_view, name='about'),
    path('terms/', views.terms_view, name='terms'),
    path('contact/', views.contact_view, name='contact'),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
