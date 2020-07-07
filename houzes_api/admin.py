from django.contrib import admin
from rangefilter.filter import DateRangeFilter
import csv
from django.http import HttpResponse

from api.models import User, UpgradeProfile, AffliateUser, CouponUser, Setting


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


class AffliateUserModel(admin.ModelAdmin):
    fields = ['email', 'first_name', 'last_name', 'phone_number', 'code', 'is_active']
    list_display = ['email', 'first_name', 'last_name', 'code', 'phone_number', 'is_active', 'created_at']
    list_filter = ['email', ]
    search_fields = ['email', 'first_name', 'last_name', 'phone_number', 'code']
    actions_on_top = False
    actions_on_bottom = True
    list_per_page = 10
    list_max_show_all = 20

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:  # You may have to check some other attrs as well
            # Editing an object
            return ('email', 'code', 'created_at')
        else:
            # Creating a new object
            return ()

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class CouponUserModel(admin.ModelAdmin):
    fields = ['email', 'first_name', 'last_name', 'code', 'activity_date']
    list_display = ['email', 'fullname', 'affiliate_user_name', 'total_amount', 'user_discount', 'affiliate_commission', 'code', 'activity_date']
    list_filter = (
        ('activity_date', DateRangeFilter),
    )
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'affiliate_user__code', 'affiliate_user__first_name', 'affiliate_user__last_name']
    actions = ['export_as_csv']
    actions_on_top = True
    actions_on_bottom = False
    list_per_page = 10
    list_max_show_all = 20

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def fullname(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name

    def email(self, obj):
        return obj.user.email

    def code(self, obj):
        return obj.affiliate_user.code

    def user_discount(self, obj):
        return obj.discount

    def affiliate_commission(self, obj):
        return obj.commission

    def affiliate_user_name(self, obj):
        return obj.affiliate_user.first_name + ' ' + obj.affiliate_user.last_name

    def export_as_csv(self, request, queryset):
        field_names = self.list_display
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format('coupon_user')
        writer = csv.writer(response)

        writer.writerow(field_names)
        for s in queryset:
            fullname = s.user.first_name + ' ' + s.user.last_name
            affiliate_user_name = s.affiliate_user.first_name + ' ' + s.affiliate_user.last_name
            activity_date = s.activity_date.strftime("%Y-%m-%d")
            writer.writerow([s.user.email, fullname, affiliate_user_name, s.total_amount, s.discount, s.commission, s.affiliate_user.code, activity_date])
        return response

    export_as_csv.short_description = "Export as CSV"


class SettingModel(admin.ModelAdmin):
    fields = ['key', 'value']
    list_display = ['key_name', 'key_value']
    search_fields = ['key']
    readonly_fields = ['key']
    actions_on_top = False
    actions_on_bottom = True
    list_per_page = 10
    list_max_show_all = 20

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def key_name(self, obj):
        return obj.key

    def key_value(self, obj):
        if obj.value:
            return str(obj.value) + ' %'
        else:
            return obj.value

    key_name.short_description = 'Key Name'
    key_value.short_description = 'Value (%)'


admin_site = MyAdminSite()
admin_site.register(User, AdminUserModel)
admin_site.register(UpgradeProfile, UpgradeProfileModel)
admin_site.register(AffliateUser, AffliateUserModel)
admin_site.register(CouponUser, CouponUserModel)
admin_site.register(Setting, SettingModel)
