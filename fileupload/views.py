from rest_framework import generics, permissions, status
from rest_framework.response import Response

from fileupload.models import UploadFile
from fileupload.serializers import FileDetailSerializer

import os


class UploadFileView(generics.CreateAPIView):
    queryset = UploadFile.objects.all()
    serializer_class = FileDetailSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def create(self, request):
        files = request.FILES.getlist("file")
        all_files = []
        for file in files:
            if file.size > 15360 * 1024:
                return Response(
                    {'details': 'File is too large'},
                    status=status.HTTP_400_BAD_REQUEST)

            allowed_extension = ['.jpeg', '.jpg', '.png', '.pdf']
            extension = os.path.splitext(file.name)[1]
            if extension not in allowed_extension:
                return Response(
                    {"details": f"Invalid file format. Kindly upload {','.join(allowed_extension)} only"},
                    status=status.HTTP_400_BAD_REQUEST)
            file_param = {
                "file": file,
                "filename": file.name,
            }
            file_inst = UploadFile.objects.create(**file_param)
            all_files.append({
                "id": file_inst.id,
                "filename": file_inst.filename,
            })

        return Response(all_files)


class FileDetailsView(generics.ListAPIView):
    serializer_class = FileDetailSerializer

    def get_queryset(self):
        payload = self.request.query_params.dict()
        _files = payload.get('file', None)
        if not _files:
            return []
        files = _files.split(',')
        file_query = UploadFile.objects.filter(
            id__in=files).order_by('-date_created')
        return file_query
