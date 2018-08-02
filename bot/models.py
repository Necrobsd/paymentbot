from django.db import models


class Product(models.Model):
    """
    Класс модели для товаров
    """
    name = models.CharField(verbose_name='Название товара',
                            max_length=100)
    description = models.TextField(verbose_name='Описание',
                                   blank=True)
    image = models.ImageField(verbose_name='Фото товара',
                              upload_to='products')
    price = models.DecimalField(verbose_name='Цена',
                                max_digits=7, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Order(models.Model):
    """
    Класс модели для заказа
    """
    client_name = models.CharField(verbose_name='Имя клиента',
                                   max_length=100)
    address = models.CharField(verbose_name='Адрес доставки',
                               max_length=254, default='')
    phone = models.CharField(verbose_name='Телефон',
                             max_length=11, default='')
    email = models.CharField(verbose_name='Email',
                             max_length=50, default='')
    date = models.DateTimeField(verbose_name='Дата заказа',
                                auto_now=True)
    total_cost = models.DecimalField(verbose_name='Общая стоимость',
                                     max_digits=7, decimal_places=2)
    is_paid = models.BooleanField(verbose_name='Статус оплаты',
                                  default=False)

    def __str__(self):
        return 'Заказ №{}'.format(self.id)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderItem(models.Model):
    """
    Класс модели, описывающий позиции в заказе
    """
    order = models.ForeignKey(Order, related_name='items',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Товар',
                                on_delete=models.CASCADE)
    count = models.PositiveSmallIntegerField(verbose_name='Количество')

    def __str__(self):
        return 'Заказ №{}: {}'.format(self.order.id, self.product.name)

    def get_cost(self):
        """
        Функция расчета стоимости позиции
        :return: float
        """
        return self.product.price * self.count

    class Meta:
        verbose_name = 'Позиция в заказе'
        verbose_name_plural = 'Позиции в заказе'
