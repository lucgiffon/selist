from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from .models import Message
from .models import Trade


def main(request):
    initiation_messages = (
        Message.objects.filter(type="initiation").select_related("trade", "user").all()
    )
    print(initiation_messages)
    return render(
        request, "chat/main.html", {"initiation_messages": initiation_messages}
    )


@csrf_exempt
@login_required
def create_trade(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        trade_type = data.get('type', '')
        
        if not message_text:
            return JsonResponse({'error': 'Message text is required'}, status=400)
        
        if trade_type not in ['offer', 'demand']:
            return JsonResponse({'error': 'Invalid trade type'}, status=400)
        
        trade = Trade.objects.create(
            initiator=request.user,
            type=trade_type
        )
        
        message = Message.objects.create(
            text=message_text,
            user=request.user,
            trade=trade,
            type='initiation'
        )
        
        return JsonResponse({
            'success': True,
            'trade_id': trade.id,
            'message_id': message.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
