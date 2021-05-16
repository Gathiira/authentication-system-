from rest_framework import renderers
import json


class CustomRenderer(renderers.JSONRenderer):

    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = ''

        if 'ErrorDetail' in str(data):
            response = json.dumps({'details': data})
        else:
            response = json.dumps({"details": data})
        return response