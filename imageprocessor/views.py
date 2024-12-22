from django.shortcuts import render, redirect,get_object_or_404
from .forms import ImageUploadForm
from .models import UploadedImage
from django.conf import settings
import pytesseract
import re 
from django.db.models import Max
from django.http import JsonResponse
from PIL import Image, ImageEnhance, ImageFilter
from django.core.files.storage import default_storage
import requests
from cloudinary.uploader import destroy
# import os

# if os.name == "nt":  # Windows
#     pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# else:  # Linux (Docker)
#     pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"





def extract_farmer_id(text):

    # Regex pattern to match 'Note:' followed by any characters and extract numeric values only
    farmer_id_pattern = r"Note\s*:\s*.*?(\d+)"

    print(f"Extracting Farmer ID from text:\n{text}\n")  # Debugging: Print the input text
    match = re.search(farmer_id_pattern, text, re.IGNORECASE)

    if match:
        farmer_id = match.group(1)
        print(f"Farmer ID Found: {farmer_id}")  # Debugging: Print extracted Farmer ID
        return farmer_id

    print("No Farmer ID found.")  # Debugging: Indicate no match
    return None



def extract_coordinates(text):
    latitude = None
    longitude = None
    
    # Improved regex patterns to capture Latitude and Longitude values
    latitude_pattern = r"(?:Latitude|latitude|Lat|ude)\s*[:\-]?\s*([-+]?\d*\.?\d+)"
    longitude_pattern = r"(?:Longitude|longitude|Long)\s*[:\-]?\s*([-+]?\d*\.\d+|\d+)"

    # Search for latitude and longitude using regex
    latitude_match = re.search(latitude_pattern, text, re.IGNORECASE)
    longitude_match = re.search(longitude_pattern, text, re.IGNORECASE)

    # Process latitude (if found)
    if latitude_match:
        latitude_value = float(latitude_match.group(1))
        
        # If latitude has an integer form, e.g., 18370791.0, convert it to a decimal
        if latitude_value.is_integer():
            latitude = latitude_value / 1000000  # Convert to decimal format
        else:
            latitude = latitude_value

    # Process longitude (if found)
    if longitude_match:
        longitude = float(longitude_match.group(1))

    return latitude, longitude



def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.save()

            try:
                # Use the image for OCR processing
                image_url = uploaded_image.image.url  # Cloudinary URL
                image = Image.open(requests.get(image_url, stream=True).raw)

                # OCR Processing using pytesseract
                extracted_text = pytesseract.image_to_string(image)
                uploaded_image.extracted_text = extracted_text.strip()

                # Check if text was extracted
                if not extracted_text.strip():
                    destroy(uploaded_image.image.public_id)  # Delete image from Cloudinary
                    uploaded_image.delete()
                    return render(request, 'imageprocessor/upload_image.html', {
                        'form': form,
                        'error': 'No valid text found in the uploaded image. Please upload a clearer image.',
                    })

                # Extract Farmer ID
                farmer_id = extract_farmer_id(extracted_text)
                if not farmer_id:
                    destroy(uploaded_image.image.public_id)
                    uploaded_image.delete()
                    return render(request, 'imageprocessor/upload_image.html', {
                        'form': form,
                        'error': 'Farmer ID not found in the uploaded image.',
                    })

                # Check for duplicate Farmer ID
                if UploadedImage.objects.filter(farmer_id=farmer_id).exists():
                    destroy(uploaded_image.image.public_id)
                    uploaded_image.delete()
                    return render(request, 'imageprocessor/upload_image.html', {
                        'form': form,
                        'error': f'Duplicate data! Farmer ID {farmer_id} has already been uploaded.',
                    })

                # Save Farmer ID and coordinates
                uploaded_image.farmer_id = farmer_id
                latitude, longitude = extract_coordinates(extracted_text)
                uploaded_image.latitude = latitude
                uploaded_image.longitude = longitude
                uploaded_image.save()

                return redirect('display_images')

            except Exception as e:
                # Handle other errors (e.g., network issues)
                destroy(uploaded_image.image.public_id)
                uploaded_image.delete()
                return render(request, 'imageprocessor/upload_image.html', {
                    'form': form,
                    'error': f'An error occurred: {str(e)}',
                })

    else:
        form = ImageUploadForm()

    return render(request, 'imageprocessor/upload_image.html', {'form': form})





def display_images(request):
    images = UploadedImage.objects.all()
    return render(request, 'imageprocessor/display_images.html', {'images': images})




def get_map_data(request):
    images = UploadedImage.objects.all()
    data = []
    
    for image in images:
        data.append({
            'id': image.id,
            'latitude': image.latitude,
            'longitude': image.longitude,
            'extracted_text': image.extracted_text,
            'image_url': image.image.url,
        })
    
    return JsonResponse(data, safe=False)

def delete_image(request, image_id):
        image_record = get_object_or_404(UploadedImage, id=image_id)
        
        # Delete the associated file from storage
        if image_record.image:
            # image_record.image.delete(save=False)  # This deletes the file from the media folder
            destroy(image_record.image.public_id)
        # Delete the record from the database
        image_record.delete()

        return redirect('display_images')  # Redirect back to the image display page    