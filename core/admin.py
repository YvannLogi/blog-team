from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

# 1. Formulaire personnalisé pour la CREATION d'un utilisateur dans l'admin
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('phone', 'first_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        # Assurez-vous que le mot de passe est bien haché si géré par le form
        if commit:
            user.save()
        return user

# 2. Formulaire personnalisé pour la MODIFICATION d'un utilisateur dans l'admin
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('phone', 'first_name', 'email', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')

# 3. Configuration de l'Admin principal
@admin.register(User) 
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # Les champs affichés dans la liste des utilisateurs
    list_display = ('phone', 'first_name', 'is_staff', 'is_active', 'is_superuser')
    
    # Les filtres sur le côté droit de la liste
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    
    # Barre de recherche
    search_fields = ('phone', 'first_name', 'email')
    
    # Tri par défaut dans la liste
    ordering = ('phone',)

    # Organisation des champs lorsque l'on clique sur un utilisateur pour le modifier
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'email')}),
        ('Permissions et Rôles', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Dates importantes', {'fields': ('last_login',)}),
    )

    # Organisation des champs pour l'écran de création d'un utilisateur (bouton "Ajouter")
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'first_name', 'email', 'password1', 'password2'),
        }),
    )