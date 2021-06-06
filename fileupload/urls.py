from fileupload.views import UploadFileView, FileDetailsView
from django.conf.urls import url


urlpatterns = [
    url('upload-file', UploadFileView.as_view(), name='upload-file'),
    url('get-file', FileDetailsView.as_view(), name='get-file'),
]
