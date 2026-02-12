from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

admin.site.site_header = "Dorixona Admin"
admin.site.site_title = "Dorixona Admin Panel"
admin.site.index_title = "Boshqaruv paneli"

urlpatterns = [
    path('admin/', admin.site.urls),

    # OpenAPI schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # ReDoc (ixtiyoriy, lekin professional)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API v1
    path('api/v2/users/', include('users.urls')),
    path('api/v1/products/', include('products.urls')),
    path('api/v3/orders/', include('orders.urls')),
    path('api/v6/payments/', include('payments.urls')),
    path('api/v4/delivery/', include('delivery.urls')),
    path('api/v5/notifications/', include('notifications.urls')),
    path('api/v7/', include('prescriptions.urls')),
    path('api/v8/', include('dashboard.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
