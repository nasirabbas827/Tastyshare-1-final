from django.db import models

class CustomerUser(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # hashed password
    full_name = models.CharField(max_length=150, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        blank=True,
        null=True
    )
    dob = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=[('active', 'Active'), ('inactive', 'Inactive'), ('banned', 'Banned')],
        default='active'
    )
    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class Recipe(models.Model):
    CATEGORY_CHOICES = [
        ('Vegetarian', 'Vegetarian'),
        ('Vegan', 'Vegan'),
        ('Non-Vegetarian', 'Non-Vegetarian'),
        ('Desserts', 'Desserts'),
        ('Snacks', 'Snacks'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey('CustomerUser', on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=255)
    description = models.TextField()
    ingredients = models.TextField()
    steps = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    cooking_time = models.PositiveIntegerField(help_text="Time in minutes")
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



class Comment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey('CustomerUser', on_delete=models.CASCADE, related_name='comments')
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name='comments')
    rating = models.PositiveSmallIntegerField()  # 1–5 stars
    text = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} - {self.recipe.title} ({self.rating})"



class Favorite(models.Model):
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} favorited {self.recipe.title}"
    

