from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from datetime import date

baskets_list=[
    {
        'id': 1,
        'items': [1, 2],
        'launch_date': '2024-12-01'
    },
    {
        'id': 2,
        'items': [],
        'launch_date': '2024-12-01'
    }
]

satellite_list = [
    {
        'id': 1,
        'title': '«Метеор-М» № 2',
        'description': 'Вторая серия космических аппаратов гидрометеорологического обеспечения.',
        'weight': 'Масса: 2778 кг',
        'image': 'http://localhost:9000/bucket/1.png',
        'full_desc': '«Метеор-М» № 2 (автоматические космические аппараты) — вторая серия космических аппаратов гидрометеорологического обеспечения. Входят в состав космического комплекса (КК) гидрометеорологического и океанографического обеспечения «Метеор-3М». Предназначены для оперативного получения информации в целях прогноза погоды, контроля озонового слоя и радиационной обстановки в околоземном космическом пространстве, а также для мониторинга морской поверхности, включая ледовую обстановку.'
    },
    {
        'id': 2,
        'title': '«Гонец-М»',
        'description': 'Система для оказания услуг связи в глобальном масштабе.',
        'weight': 'Масса: 280 кг',
        'image': 'http://localhost:9000/bucket/2.png',
        'full_desc': '«Гонец-М» — российская многофункциональная система персональной спутниковой связи (МСПСС), построенная на базе низкоорбитальных космических аппаратов. Назначением системы является оказание услуг связи в глобальном масштабе. Система разрабатывается по заказу Федерального космического агентства России. Головным разработчиком является АО «Информационные спутниковые системы имени академика М. Ф. Решетнёва», оператором и эксплуатирующей организацией — АО «Спутниковая система „Гонец“».'
    },
    {
        'id': 3,
        'title': '«Кондор-ФКА»',
        'description': 'Картографирование, экологический мониторинг и разведка природных ресурсов.',
        'weight': 'Масса: 1050 кг',
        'image': 'http://localhost:9000/bucket/3.png',
        'full_desc': 'Система предназначена для получения высококачественных изображений, необходимых для мониторинга земной поверхности и океанов, экологического мониторинга и эффективного управления природными ресурсами. Космическая система «Кондор» на базе малых космических аппаратов (КА) обеспечивает: картографирование территорий, изучение и контроль природных ресурсов, океанологические исследования прибрежных акваторий и шельфовых зон, экологические исследования, информационное обеспечение при чрезвычайных ситуациях. Спутники «Кондор» построены по модульному принципу и состоят из базовой унифицированной космической платформы и модуля полезной нагрузки, в качестве которой могут быть использованы радиолокатор с синтезированной апертурой, оптико-электронная аппаратура, научная аппаратура.'
    }
]

def mainPage(request):
    basket_id = 1

    basket_count = 0
    for basket in baskets_list:
        if basket['id'] == basket_id:
            basket_count = len(basket['items'])

    search_query = request.GET.get('search', '')
    if search_query:
        filtered_orders = [order for order in satellite_list if search_query.lower() in order['title'].lower()]
    else:
        filtered_orders = satellite_list

    context = {
        'data': {
            'orders': filtered_orders,
            'BasketCount': basket_count,
            'Basket_id': basket_id,
            'basket_count':basket_count,
        }
    }

    return render(request, 'orders.html', context)

def BasketCreator(request, id):
    satellite_list_basket = []

    basket_id = 1

    for basket in baskets_list:
        if basket['id'] == id:
            for i in basket['items']:
                for satellite in satellite_list:
                    if satellite['id'] == i:
                        satellite_list_basket.append(satellite)

    return render(request, 'basket.html', {'data' : {
        'id': id,
        'baskets': baskets_list,
        'orders': satellite_list_basket
    }})

def SatPage(request, id):
    return render(request, 'order.html', {'data' : {
        'order' : satellite_list[id-1],
        'id': id
    }})