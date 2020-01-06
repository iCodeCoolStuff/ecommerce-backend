from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
<<<<<<< HEAD
from .models import User, ImageSet, Product
=======
from .models import User, ImageSet, Order
>>>>>>> fd46e7f... register order model in admin


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)
<<<<<<< HEAD
admin.site.register(Product)
admin.site.register(ImageSet)
=======
admin.site.register(ImageSet)
admin.site.register(Order)
>>>>>>> fd46e7f... register order model in admin
