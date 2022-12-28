from django.shortcuts import render

from django.http import HttpResponse


items = [{"day": '11-02-2022', "yawns": 5, "eyes": 10}, {"day": '12-02-2022', "yawns": 4, "eyes": 8}, {"day": '13-02-2022', "yawns": 11, "eyes": 14}]

def tiredness(request):
    context = {
        'message': 'These are your tiredness stats',
        'items': items,
        'chart_data': {
    'labels': [item['day'] for item in items],
    'datasets': [{
        'label': 'Yawns',
        'data': [item['yawns'] for item in items],
        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
        'borderColor': 'rgba(255, 99, 132, 1)',
    }]
}
    }
    return render(request, 'tiredness_stats.html', context)