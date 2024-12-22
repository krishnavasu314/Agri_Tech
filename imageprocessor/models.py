from django.db import models
from cloudinary.models import CloudinaryField

class UploadedImage(models.Model):

    # image = models.ImageField(upload_to='uploaded_images/')
    image = CloudinaryField('image')
    farmer_id = models.CharField(max_length=255, null=False, blank=False )
    extracted_text = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(blank=False, null=True)
    longitude = models.FloatField(blank=False, null=True)

    def __str__(self):
        return f"Farmer ID: {self.farmer_id} | Uploaded At: {self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['farmer_id'], name='unique_farmer_id_constraint')
        ]
