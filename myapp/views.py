from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import CustomerUser, Recipe, Comment, Favorite
from .forms import RegisterForm, LoginForm, EditProfileForm, RecipeForm, CommentForm , ChangePasswordForm
from django.core.mail import send_mail
from django.conf import settings



# =====================================================
#                AUTHENTICATION VIEWS
# =====================================================

from django.shortcuts import render
from django.db.models import Q, Count
from .models import Recipe, CustomerUser

def index(request):
    """Render homepage with approved recipes, search, filter, and sort options."""

    # Get query parameters
    query = request.GET.get('q', '').strip()  # Search query
    category = request.GET.get('category', '')  # Filter by category
    sort_by = request.GET.get('sort_by', 'recent')  # Sort by 'recent' or 'popular'

    # Start with approved recipes
    recipes = Recipe.objects.filter(status='Approved')

    # Search across title, ingredients, category, and cooking_time
    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(ingredients__icontains=query) |
            Q(category__icontains=query) |
            Q(cooking_time__icontains=query)
        )

    # Filter by category (dietary preferences)
    if category in ['Vegetarian', 'Vegan', 'Non-Vegetarian', 'Desserts', 'Snacks']:
        recipes = recipes.filter(category=category)

    # Sort recipes
    if sort_by == 'popular':
        recipes = recipes.annotate(favorite_count=Count('favorited_by')).order_by('-favorite_count', '-created_at')
    else:  # Default to 'recent'
        recipes = recipes.order_by('-created_at')

    # Categories for filter dropdown
    categories = Recipe.CATEGORY_CHOICES

    return render(request, 'index.html', {
        'recipes': recipes,
        'query': query,
        'selected_category': category,
        'sort_by': sort_by,
        'categories': categories,
    })



def register_view(request):
    """Handle user registration."""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. Please login.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    """Custom login logic using session-based authentication."""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = CustomerUser.objects.get(username=username)

                # Check user account status
                if user.status != 'active':
                    messages.error(request, "Your account is not active. Please contact support.")
                elif check_password(password, user.password):
                    # Login success → store user info in session
                    request.session['user_id'] = user.user_id
                    request.session['username'] = user.username
                    messages.success(request, f"Welcome {user.username}!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Invalid password")

            except CustomerUser.DoesNotExist:
                messages.error(request, "User not found")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """Logout user and clear session."""
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect('index')


from django.db.models import Q, Count
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomerUser, Recipe

def dashboard_view(request):
    """Dashboard showing all approved recipes with search, filter, and sort options."""
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user = CustomerUser.objects.get(user_id=request.session['user_id'])

    # Get query parameters
    query = request.GET.get('q', '').strip()  # Search query
    category = request.GET.get('category', '')  # Filter by category
    sort_by = request.GET.get('sort_by', 'recent')  # Sort by 'recent' or 'popular'

    # Start with approved recipes
    recipes = Recipe.objects.filter(status='Approved')

    # Search across title, ingredients, category, and cooking_time
    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(ingredients__icontains=query) |
            Q(category__icontains=query) |
            Q(cooking_time__icontains=query)
        )

    # Filter by dietary preferences
    if category in ['Vegetarian', 'Vegan', 'Non-Vegetarian']:
        recipes = recipes.filter(category=category)

    # Sort recipes
    if sort_by == 'popular':
        recipes = recipes.annotate(favorite_count=Count('favorited_by')).order_by('-favorite_count', '-created_at')
    else:  # Default to 'recent'
        recipes = recipes.order_by('-created_at')

    # Get all categories for the filter dropdown
    categories = Recipe.CATEGORY_CHOICES

    return render(request, 'dashboard.html', {
        'user': user,
        'recipes': recipes,
        'query': query,
        'selected_category': category,
        'sort_by': sort_by,
        'categories': categories,
    })



# =====================================================
#                   PROFILE MANAGEMENT
# =====================================================

def edit_profile(request):
    """Allow user to edit their profile information."""
    if not request.session.get('user_id'):
        messages.error(request, "You need to log in first.")
        return redirect('login')

    user = get_object_or_404(CustomerUser, pk=request.session['user_id'])

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('dashboard')
    else:
        form = EditProfileForm(instance=user)

    return render(request, 'edit_profile.html', {
        'form': form,
        'user': user,
    })


# =====================================================
#                   RECIPE CRUD VIEWS
# =====================================================

def recipe_list(request):
    """Display all recipes added by the logged-in user."""
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user = CustomerUser.objects.get(user_id=request.session['user_id'])
    recipes = Recipe.objects.filter(user=user).order_by('-created_at')

    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})



def recipe_create(request):
    """Allow logged-in users to add a new recipe (auto-pending)."""
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user = CustomerUser.objects.get(user_id=request.session['user_id'])

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user = user
            recipe.status = 'Pending'  # new recipes pending approval
            recipe.save()
            messages.success(request, "Recipe submitted and awaiting admin approval.")
            return redirect('dashboard')
    else:
        form = RecipeForm()

    return render(request, 'recipes/recipe_form.html', {'form': form, 'title': 'Add Recipe'})


def recipe_update(request, pk):
    """Allow users to edit their own recipes (re-pending after edit)."""
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    recipe = get_object_or_404(Recipe, pk=pk, user_id=request.session['user_id'])

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            updated_recipe = form.save(commit=False)
            updated_recipe.status = 'Pending'  # reset to pending after edit
            updated_recipe.save()
            messages.success(request, "Recipe updated and resubmitted for approval.")
            return redirect('dashboard')
    else:
        form = RecipeForm(instance=recipe)

    return render(request, 'recipes/recipe_form.html', {'form': form, 'title': 'Edit Recipe'})


def recipe_delete(request, pk):
    """Allow users to delete their own recipes."""
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    recipe = get_object_or_404(Recipe, pk=pk, user_id=request.session['user_id'])

    if request.method == 'POST':
        recipe.delete()
        messages.success(request, "Recipe deleted successfully.")
        return redirect('dashboard')

    return render(request, 'recipes/recipe_confirm_delete.html', {'recipe': recipe})


# =====================================================
#           RECIPE DETAIL + COMMENTS + FAVORITES
# =====================================================

from django.core.mail import send_mail
from django.conf import settings

def recipe_detail(request, pk):
    """
    Display recipe details.
    Handle comment creation, favorites, and email alert for new comments.
    """
    recipe = get_object_or_404(Recipe, pk=pk, status='Approved')  # only approved recipes visible

    # Check if user is logged in
    user = None
    is_favorite = False
    if 'user_id' in request.session:
        user = CustomerUser.objects.get(user_id=request.session['user_id'])
        is_favorite = Favorite.objects.filter(user=user, recipe=recipe).exists()

    # Load only approved comments
    comments = recipe.comments.select_related("user").filter(status='Approved').order_by("-created_at")

    # Handle comment submission
    if request.method == "POST" and user:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment, created = Comment.objects.update_or_create(
                user=user,
                recipe=recipe,
                defaults={
                    "rating": form.cleaned_data["rating"],
                    "text": form.cleaned_data["text"],
                    "status": "Pending",  # pending approval
                }
            )

            messages.success(request, "Your comment was submitted for review.")

            # Send email alert to recipe owner (even if pending)
            if recipe.user.email and recipe.user != user:
                subject = f"New comment on your recipe: {recipe.title}"
                message = f"Hi {recipe.user.full_name or recipe.user.username},\n\n" \
                          f"{user.username} commented on your recipe '{recipe.title}'.\n\n" \
                          f"Comment: {comment.text}\n\n" \
                          "Log in to review and approve the comment."
                recipient_list = [recipe.user.email]

                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
                except Exception as e:
                    print(f"Failed to send email: {e}")

            return redirect("recipe_detail", pk=pk)
    else:
        form = CommentForm()

    return render(request, "recipe_detail.html", {
        "recipe": recipe,
        "comments": comments,
        "form": form,
        "is_favorite": is_favorite,
    })


# =====================================================
#                   FAVORITES VIEWS
# =====================================================

def toggle_favorite(request, pk):
    """Toggle (add/remove) a recipe from user's favorites."""
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect("login")

    user = CustomerUser.objects.get(user_id=request.session['user_id'])
    recipe = get_object_or_404(Recipe, pk=pk, status='Approved')

    favorite, created = Favorite.objects.get_or_create(user=user, recipe=recipe)
    if not created:
        favorite.delete()
        messages.info(request, "Recipe removed from favorites.")
    else:
        messages.success(request, "Recipe added to favorites.")

    return redirect("recipe_detail", pk=pk)


def favorites_view(request):
    """Display all favorite recipes of the logged-in user."""
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect("login")

    user = CustomerUser.objects.get(user_id=request.session['user_id'])
    favorites = Favorite.objects.filter(user=user, recipe__status='Approved').select_related("recipe")

    return render(request, "favorites.html", {"favorites": favorites})


# =====================================================
#                   STATIC PAGES
# =====================================================

def about_view(request):
    """Render the About page."""
    return render(request, 'about.html')


def terms_view(request):
    """Render the Terms & Conditions page."""
    return render(request, 'terms.html')


def contact_view(request):
    """Render the Contact Us page."""
    return render(request, 'contact.html')


from django.contrib import messages

from django.core.mail import send_mail
from django.conf import settings

# ------------------- Change Password -------------------
def change_password(request):
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user = CustomerUser.objects.get(user_id=request.session['user_id'])

    if request.method == "POST":
        form = ChangePasswordForm(user, request.POST)
        if form.is_valid():
            user.password = form.cleaned_data['new_password']
            user.save()

            # Send email notification
            if user.email:
                subject = "TastShare Plateform- Your password has been changed/Reset"
                message = f"Hi {user.full_name or user.username},\n\n" \
                          "This is a confirmation that your account password has been successfully changed.\n\n" \
                          "If you did not perform this action, please contact support immediately."
                recipient_list = [user.email]
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
                except Exception as e:
                    print(f"Failed to send email: {e}")

            messages.success(request, "Password changed successfully! A confirmation email has been sent.")
            return redirect('edit_profile')
    else:
        form = ChangePasswordForm(user)

    return render(request, 'change_password.html', {'form': form})


# ------------------- Delete Account -------------------
def delete_account(request):
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user = CustomerUser.objects.get(user_id=request.session['user_id'])

    if request.method == "POST":
        user.delete()
        request.session.flush()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('index')

    return render(request, 'delete_account.html', {'user': user})




