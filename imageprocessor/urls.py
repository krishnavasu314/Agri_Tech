from django.urls import path
from . import views


from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.upload_image, name='upload_image'),
    path('display/', views.display_images, name='display_images'),
    path('map_data/', views.get_map_data, name='get_map_data'),
    path('delete-image/<int:image_id>/', views.delete_image, name='delete_image'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)