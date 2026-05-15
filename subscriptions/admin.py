from django.contrib import admin
from .models import Category, Subscription, SubscriptionHistory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color')
    search_fields = ('name',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'category', 'price', 'currency', 'billing_cycle', 'status', 'renewal_date')
    list_filter = ('status', 'billing_cycle', 'currency', 'category', 'created_at')
    search_fields = ('name', 'user__email')
    date_hierarchy = 'created_at'


@admin.register(SubscriptionHistory)
class SubscriptionHistoryAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('subscription__name',)
