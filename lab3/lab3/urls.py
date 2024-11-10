from django.contrib import admin
from launchesapp import views
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),

    path(r'satellites/', views.SatList.as_view(), name='satellites-list'),
    path(r'satellites/<int:satellite_id>', views.SatDetail.as_view(), name='satellites-detail'),
    path(r'satellites/<int:satellite_id>/addimg', views.SatImgUpload, name='add-sat-img'),

    path(r'launches/', views.LaunchesList.as_view(), name='launches-list'),
    path(r'launches/<int:launch_id>', views.LaunchDetail.as_view(), name='launch-detail'),
    path(r'launches/<int:launch_id>/form', views.CreatorSave.as_view(), name='launch-form'),
    path(r'launches/<int:launch_id>/mod', views.ModAccept.as_view(), name='launch-mod'),

    path(r'satlaunch/<int:satellite_id>/<int:launch_id>', views.SatLaunch.as_view(), name = 'sat-launch'),

    #path(r'users/', views.UsersList.as_view(), name='users-list'),

    path(r'user/register', views.UserDetail.as_view(), name='user-reg'),
    path(r'user/<int:user_id>', views.UserDetail.as_view(), name='user-detail'),
    path(r'user/login', views.UserLogin.as_view(), name='user-login'),
    path(r'user/logout', views.UserLogout.as_view(), name='user-logout'),
]