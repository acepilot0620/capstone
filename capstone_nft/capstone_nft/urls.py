from django.contrib import admin
from django.urls import path, include
from dj_rest_auth.views import LoginView, LogoutView
from dj_rest_auth.registration.views import RegisterView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg       import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Capstone NFT 민팅 서버",
        default_version='-',
        description="Capstone NFT 민팅 서버",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
    

urlpatterns = [
    path(r'swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(r'swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-v1'),
    path('admin/', admin.site.urls),
    
    # 로그인/회원가입
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('signup/', RegisterView.as_view()),

    # 하위 앱
    path('user/', include('user.urls')),
    path('nft/', include('nft.urls')),
]