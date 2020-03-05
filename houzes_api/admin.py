from django.contrib import admin

from api.models import User, UpgradeProfile


class MyAdminSite(admin.AdminSite):
    site_header = 'Houzes Admin Panel'
    site_title = 'Houzes Admin Panel'
    index_title = 'Houzes Admin'


class AdminUserModel(admin.ModelAdmin):
    fields = ['first_name', 'last_name', 'email', 'phone_number', 'is_active', 'created_at']
    readonly_fields = ['email', 'created_at']
    list_display = ['email', 'first_name', 'last_name', 'phone_number', 'created_at']
    list_filter = ['email', ]
    search_fields = ['email', 'first_name', 'last_name', ]
    actions_on_top = False
    actions_on_bottom = True
    list_per_page = 10
    list_max_show_all = 20

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class UpgradeProfileModel(admin.ModelAdmin):
    fields = ['user', 'plan', 'coin', 'expire_at', 'created_at']
    readonly_fields = ['user', 'created_at']
    list_display = ['user', 'coin', 'plan', 'first_name', 'last_name', 'phone_number', 'created_at']
    list_select_related = ['plan']
    list_filter = ['user', ]
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    actions_on_top = False
    actions_on_bottom = True
    list_per_page = 10
    list_max_show_all = 20

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name

    def phone_number(self, obj):
        return obj.user.phone_number

    first_name.short_description = 'First Name'
    first_name.admin_order_field = 'user__first_name'
    last_name.short_description = 'Last Name'
    last_name.admin_order_field = 'user__last_name'
    phone_number.short_description = 'Phone Number'
    phone_number.admin_order_field = 'user__phone_number'



admin_site = MyAdminSite()
admin_site.register(User, AdminUserModel)
admin_site.register(UpgradeProfile, UpgradeProfileModel)
