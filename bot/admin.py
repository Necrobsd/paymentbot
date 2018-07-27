from django.contrib import admin
from bot.models import Product, Order, OrderItem


class InlineItemsOrderAdmin(admin.TabularInline):
    model = OrderItem
    readonly_fields = fields = ['product', 'get_price', 'count', 'get_cost']
    max_num = 0

    def get_cost(self, obj):
        """
        Функция расчета стоимости позиции
        :return: float
        """
        return obj.product.price * obj.count

    def get_price(self, obj):
        return obj.product.price

    get_price.short_description = 'Цена за ед.'
    get_cost.short_description = 'Стоимость'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class OrderAdmin(admin.ModelAdmin):
    fields = ['client_name', 'address', 'phone', 'email', 'date', 'total_cost']
    readonly_fields = fields
    inlines = [InlineItemsOrderAdmin]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


admin.site.register(Product)
admin.site.register(Order, OrderAdmin)

