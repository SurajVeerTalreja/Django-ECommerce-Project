from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

# Customizing Admin Pannel
class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')

    # Non-editable fields such as below should be marked as readonly
    # Only after which those could be added into 'fieldsets' below
    readonly_fields = ('last_login','date_joined')

    ordering = ('-date_joined',)

    filter_horizontal = ()

    list_filter = ('email', 'username', 'date_joined', 'is_staff')

    # Customizing how the fields should look while selecting any user Also it makes password readonly by default.
    fieldsets = (
        ('Credentials', {'fields': ('email', 'username')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_admin', 'is_superadmin')}),
        ('Personal', {'fields': ('first_name', 'last_name')}),
        ('Information', {'fields': ('date_joined', 'last_login')}),
    )

    # Adding a New User using an Admin Pannel
    # password1 and password2 are default keywords.
    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': ('email', 'username', 'first_name', 'password1', 'password2', 'is_active', 'is_staff')
            }
        ),
    )

# Register your models here.
admin.site.register(Account, AccountAdmin)