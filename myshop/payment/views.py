import braintree
from django.shortcuts import render, redirect, get_object_or_404
from orders.models import Order


def payment_process(request):
    """Обработчик платежа"""
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        #Получение токена для создания транзакции
        nonce = request.POST.get('payment_method_nonce', None)
        #Создание и сохранение транзакции
        result = braintree.Transaction.sale({
            'amount': '{:.2f}'.format(order.get_total_cost()),
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })

        if result.is_success:
            #Отметим заказ, как оплаченный
            order.paid = True
            #Сохраняем ID транзакции в заказе
            order.braintree_id = result.transaction.id
            order.save()
            return redirect('payment:done')
        else:
            return redirect('payment:canceled')

    else:
        #Формирование одноразового токена для JavaScript SDK
        client_token = braintree.ClientToken.generate()
        return render(request,
                      'payment/process.html',
                      {'order': order,
                       'client_token': client_token})


def payment_done(request):
    """Обработчик успешной оплаты"""
    return render(request, 'payment/done.html')


def payment_canceled(request):
    """Обработчик ошибки оплаты"""
    return render(request, 'payment/canceled.html')



