from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from transbank.webpay.webpay_plus.transaction import Transaction, WebpayOptions
from transbank.common.integration_type import IntegrationType

import random


@csrf_exempt
def create_payment(request):
    if request.method == 'POST':
        try:
            # Configuración para pruebas
            options = WebpayOptions(
                commerce_code="597055555532",
                api_key="579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
                integration_type=IntegrationType.TEST
            )

            # Datos de la transacción
            buy_order = f"order_{random.randint(1000, 9999)}"
            session_id = f"session_{random.randint(1000, 9999)}"
            amount = 10000
            return_url = "http://localhost:8000/payments/response/"

            # Crear transacción
            tx = Transaction(options)
            response = tx.create(
                buy_order=buy_order,
                session_id=session_id,
                amount=amount,
                return_url=return_url
            )

            # Convertir NamedTuple a dict si es necesario
            if hasattr(response, '_asdict'):
                response = response._asdict()

            return JsonResponse({
                'token': response['token'],
                'url': response['url']
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'type': type(e).__name__
            }, status=500)


@csrf_exempt
def payment_response(request):
    token = request.GET.get('token_ws') or request.POST.get('token_ws')
    
    if not token:
        return render(request, 'payments/error.html', {
            'error_message': 'No se recibió token de WebPay'
        })

    try:
        # Configuración para pruebas
        options = WebpayOptions(
            commerce_code="597055555532",
            api_key="579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
            integration_type=IntegrationType.TEST
        )
        
        # 1. Confirmar transacción
        tx = Transaction(options)
        response = tx.commit(token)
        
        # 2. Convertir la respuesta de forma segura
        if hasattr(response, '_fields'):  # Para namedtuple
            response_data = {field: getattr(response, field) for field in response._fields}
        elif hasattr(response, '__dict__'):  # Para objetos con __dict__
            response_data = vars(response)
        else:
            response_data = dict(response)  # Último intento
            
        # Debug
        print("Tipo de respuesta:", type(response))
        print("Datos de respuesta:", response_data)
        
        # 3. Procesamiento seguro
        status = 'Aprobado' if response_data.get('response_code') == 0 else 'Rechazado'
        
        return render(request, 'payments/result.html', {
            'status': status,
            'amount': response_data.get('amount', 'N/A'),
            'buy_order': response_data.get('buy_order', 'N/A'),
            'transaction_date': response_data.get('transaction_date', 'N/A')
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return render(request, 'payments/error.html', {
            'error_message': f"Error técnico al procesar pago. Por favor intente más tarde. Detalle: {str(e)}"
        })

def payment_form(request):
    return render(request, 'payments/payment.html')