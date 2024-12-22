from django.contrib import admin

# Register your models here.
from .models import UploadedImage

@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ( 'image',  'extracted_text','uploaded_at','longitude','latitude')
    search_fields = ('extracted_text',)
