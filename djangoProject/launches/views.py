from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from datetime import date


launches_list=[
    {
        'id': 1,
        'name': '«Союз-2.1б»',
        'items': [1, 2],
        'launch_date': '2024-12-01',
        'arrangement_order': [1, 2],
    },
    {
        'id': 2,
        'name': '«Ангара-А5П»',
        'items': [],
        'launch_date': '2024-10-21',
        'arrangement_order': [1, 2]
    }
]
satellite_list = [
    {
        'id': 1,
        'title': '«Метеор-М» № 2',
        'description': 'Вторая серия космических аппаратов гидрометеорологического обеспечения.',
        'weight': 'Масса: 2778 кг',
        'image': 'http://localhost:9000/bucket/1.png',
        'orbit': 'Круговая, солнечно-синхронная, утренняя (9:30)',
        'expected_date': '2024-12-01',
        'full_desc': '«Метеор-М» № 2 (автоматические космические аппараты) — вторая серия космических аппаратов гидрометеорологического обеспечения. Входят в состав космического комплекса (КК) гидрометеорологического и океанографического обеспечения «Метеор-3М». Предназначены для оперативного получения информации в целях прогноза погоды, контроля озонового слоя и радиационной обстановки в околоземном космическом пространстве, а также для мониторинга морской поверхности, включая ледовую обстановку.'
    },
    {
        'id': 2,
        'title': '«Гонец-М»',
        'description': 'Система для оказания услуг связи в глобальном масштабе.',
        'weight': 'Масса: 280 кг',
        'image': 'http://localhost:9000/bucket/2.png',
        'orbit': 'Высота орбиты, 1400 км; Наклонение, 82,5°',
        'expected_date': '2025-01-03',
        'full_desc': '«Гонец-М» — российская многофункциональная система персональной спутниковой связи (МСПСС), построенная на базе низкоорбитальных космических аппаратов. Назначением системы является оказание услуг связи в глобальном масштабе. Система разрабатывается по заказу Федерального космического агентства России. Головным разработчиком является АО «Информационные спутниковые системы имени академика М. Ф. Решетнёва», оператором и эксплуатирующей организацией — АО «Спутниковая система „Гонец“».'
    },
    {
        'id': 3,
        'title': '«Кондор-ФКА»',
        'description': 'Картографирование, экологический мониторинг и разведка природных ресурсов.',
        'weight': 'Масса: 1050 кг',
        'image': 'http://localhost:9000/bucket/3.png',
        'orbit': 'Околополярные солнечно-синхронные, смещенные друг от друга на 8,88°',
        'expected_date': '2024-11-14',
        'full_desc': 'Система предназначена для получения высококачественных изображений, необходимых для мониторинга земной поверхности и океанов, экологического мониторинга и эффективного управления природными ресурсами. Космическая система «Кондор» на базе малых космических аппаратов (КА) обеспечивает: картографирование территорий, изучение и контроль природных ресурсов, океанологические исследования прибрежных акваторий и шельфовых зон, экологические исследования, информационное обеспечение при чрезвычайных ситуациях. Спутники «Кондор» построены по модульному принципу и состоят из базовой унифицированной космической платформы и модуля полезной нагрузки, в качестве которой могут быть использованы радиолокатор с синтезированной апертурой, оптико-электронная аппаратура, научная аппаратура.'
    },
    {
        'id': 4,
        'title': '«Метеор-М» № 2',
        'description': 'Вторая серия космических аппаратов гидрометеорологического обеспечения.',
        'weight': 'Масса: 2778 кг',
        'image': 'http://localhost:9000/bucket/1.png',
        'orbit': 'Круговая, солнечно-синхронная, утренняя (9:30)',
        'expected_date': '2024-12-01',
        'full_desc': '«Метеор-М» № 2 (автоматические космические аппараты) — вторая серия космических аппаратов гидрометеорологического обеспечения. Входят в состав космического комплекса (КК) гидрометеорологического и океанографического обеспечения «Метеор-3М». Предназначены для оперативного получения информации в целях прогноза погоды, контроля озонового слоя и радиационной обстановки в околоземном космическом пространстве, а также для мониторинга морской поверхности, включая ледовую обстановку.'
    },
    {
        'id': 5,
        'title': '«Метеор-М» № 2',
        'description': 'Вторая серия космических аппаратов гидрометеорологического обеспечения.',
        'weight': 'Масса: 2778 кг',
        'image': 'http://localhost:9000/bucket/1.png',
        'orbit': 'Круговая, солнечно-синхронная, утренняя (9:30)',
        'expected_date': '2024-12-01',
        'full_desc': '«Метеор-М» № 2 (автоматические космические аппараты) — вторая серия космических аппаратов гидрометеорологического обеспечения. Входят в состав космического комплекса (КК) гидрометеорологического и океанографического обеспечения «Метеор-3М». Предназначены для оперативного получения информации в целях прогноза погоды, контроля озонового слоя и радиационной обстановки в околоземном космическом пространстве, а также для мониторинга морской поверхности, включая ледовую обстановку.'
    }
]

def mainPage(request):
    launch_id = 1

    launches_size = 0
    for launch in launches_list:
        if launch['id'] == launch_id:
            launches_size = len(launch['items'])

    search_query = request.GET.get('satname', '')
    if search_query:
        sats_filtered = [satellite for satellite in satellite_list if search_query.lower() in satellite['title'].lower()]
    else:
        sats_filtered = satellite_list

    context = {
        'data': {
            'search': search_query,
            'satellites': sats_filtered,
            'launchesSize': launches_size,
            'launch_id': launch_id
        }
    }

    return render(request, 'satellites.html', context)

def LaunchesCreator(request, id):
    satellite_list_basket = []
    arrangement_order = []

    for launch in launches_list:
        if launch['id'] == id:
            arrangement_order = launch['arrangement_order']
            for i in launch['items']:
                for satellite in satellite_list:
                    if satellite['id'] == i:
                        satellite_list_basket.append(satellite)

    satellites_with_order = zip(satellite_list_basket, arrangement_order)

    return render(request, 'launch.html', {'data' : {
        'launch': launches_list[id-1],
        'satellites_with_order': satellites_with_order
    }})


def SatPage(request, id):
    return render(request, 'satellite.html', {'data' : {
        'satellite' : satellite_list[id-1],
        'id': id
    }})