from django.urls import path
from .views import UploadReceiptView, upload_receipt_form

urlpatterns = [
    path("upload/", UploadReceiptView.as_view(), name="upload_receipt"),
    path("upload-receipt/", upload_receipt_form, name="upload_receipt"),
]
