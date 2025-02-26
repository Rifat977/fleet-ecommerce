from setting.models import CompanySetting

def currency_context(request):
    currency_code = CompanySetting.objects.first().currency_code        
    currency_symbol = CompanySetting.objects.first().currency_symbol

    return {
        'currency_code': currency_code,
        'currency_symbol': currency_symbol,
    }
