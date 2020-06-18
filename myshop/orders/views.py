from django.urls import reverse
from django.shortcuts import render, redirect
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created


def order_create(request):
    """Создание заказа"""
    cart = Cart(request)
    if request.method  == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            #Очищаем корзину
            cart.clear()
            #Запускаем асинхронную задачу
            order_created.delay(order.id)
            #Сохраняем заказ в сессии
            request.session['order_id'] = order.id
            #Редирект на страницу оплаты
            return redirect(reverse('payment:process'))
            """return render(request,
                          'orders/order/created.html',
                          {'order': order})"""
    else:
        form = OrderCreateForm()
    return render(request,
                  'orders/order/create.html',
                  {'cart': cart, 'form': form})

