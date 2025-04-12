import os
import pydicom
import numpy as np
from PIL import Image

def dicom_to_jpeg(dicom_path, output_path):
    # Read DICOM file
    ds = pydicom.dcmread(dicom_path)
    pixel_array = ds.pixel_array.astype(float)

    # Apply Rescale Slope and Intercept
    slope = ds.get('RescaleSlope', 1.0)
    intercept = ds.get('RescaleIntercept', 0.0)
    pixel_array = pixel_array * slope + intercept

    # Handle MONOCHROME1 inversion
    photometric = ds.get('PhotometricInterpretation', '')
    if photometric == 'MONOCHROME1':
        pixel_array = np.max(pixel_array) - pixel_array

    # Normalize to 0-255
    pixel_min = pixel_array.min()
    pixel_max = pixel_array.max()
    if pixel_max != pixel_min:  # Avoid division by zero
        pixel_array = (pixel_array - pixel_min) / (pixel_max - pixel_min) * 255.0
    else:
        pixel_array = pixel_array - pixel_min  # Results in all zeros if min == max
    pixel_array = pixel_array.astype(np.uint8)

    # Convert to PIL Image and save as JPEG
    img = Image.fromarray(pixel_array)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.save(output_path, quality=85)
    print(f"Converted DICOM to JPEG: {output_path}")

def resize_image(input_path, output_path, size=(384, 384)):
    img = Image.open(input_path)
    resized_img = img.resize(size)
    resized_img.save(output_path, quality=85)
    print(f"Resized image saved at: {output_path}")

# Main directory containing patient folders
main_dir = r'E:\mini-1\Dataset\test_images'
output_dir = r'E:\mini-1\Dataset\output\test_images'

os.makedirs(output_dir, exist_ok=True)

# Process each patient folder
for patient_id in os.listdir(main_dir):
    patient_path = os.path.join(main_dir, patient_id)
    if not os.path.isdir(patient_path):
        continue

    # Process each study folder under the patient
    for study_folder in os.listdir(patient_path):
        study_path = os.path.join(patient_path, study_folder)
        if not os.path.isdir(study_path):
            continue

        # Create output directories preserving structure
        output_study_dir = os.path.join(output_dir, patient_id, study_folder)
        os.makedirs(output_study_dir, exist_ok=True)

        # Convert and resize each DICOM file
        for dicom_file in os.listdir(study_path):
            if dicom_file.lower().endswith('.dcm'):
                dicom_path = os.path.join(study_path, dicom_file)
                base_name = os.path.splitext(dicom_file)[0]
                
                # Generate paths
                jpeg_path = os.path.join(output_study_dir, f"{base_name}.jpg")
                resized_path = os.path.join(output_study_dir, f"resized_{base_name}.jpg")

                # Perform conversion and resizing
                dicom_to_jpeg(dicom_path, jpeg_path)
                resize_image(jpeg_path, resized_path)
                print(f"Processed: {dicom_file} -> {resized_path}")

print("Dataset processing completed successfully.")