from django.contrib import admin
from rest_framework import routers
from rest_framework import permissions
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from launchesapp import views

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    ##path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path(r'satellites/', views.SatList.as_view(), name='satellites-list'),
    path(r'satellites/<int:satellite_id>', views.SatDetail.as_view(), name='satellites-detail'),
    path(r'satellites/<int:satellite_id>/addimg', views.SatImgUpload, name='add-sat-img'),

    path(r'launches/', views.LaunchesList.as_view(), name='launches-list'),
    path(r'launches/<int:launch_id>', views.LaunchDetail.as_view(), name='launch-detail'),
    path(r'launches/<int:launch_id>/form', views.CreatorSave.as_view(), name='launch-form'),
    path(r'launches/<int:launch_id>/mod', views.ModAccept.as_view(), name='launch-mod'),

    path(r'satlaunch/<int:satellite_id>/<int:launch_id>', views.SatLaunch.as_view(), name = 'sat-launch'),

    ##path(r'user/register', views.UserDetail.as_view(), name='user-reg'),
    ##path(r'user/<int:user_id>', views.UserDetail.as_view(), name='user-detail'),
    ##path(r'user/login', views.UserLogin.as_view(), name='user-login'),
    ##path(r'user/logout', views.UserLogout.as_view(), name='user-logout'),
]