from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


def get_test_image(name="test.png"):
    file = BytesIO()
    image = Image.new("RGB", (100, 100), color="white")
    image.save(file, "PNG")
    file.seek(0)

    return SimpleUploadedFile(
        name=name,
        content=file.read(),
        content_type="image/png"
    )
