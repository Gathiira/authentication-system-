import jwt
from rest_framework import authentication, exceptions
from authentication.models import User
from rest_framework import status
from usermanagement import settings as C


class SystemAuthentication(authentication.BaseAuthentication):
    def __init__(self):
        self.authentication_header_prefix = 'Bearer'

    def get_jwtauthorization_header(self, request):
        """
        Return request's 'Authorization:' header, as a bytestring.

        Hide some test client ickyness where the header can be unicode.
        """
        auth = request.headers.get('JWTAUTH', b'')
        # authparams = auth.encode(HTTP_HEADER_ENCODING)
        return auth

    def authenticate(self, request):
        request.user = None
        auth_header = self.get_jwtauthorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()
        if not auth_header:
            return None
        if len(auth_header) == 1:
            raise exceptions.NotAuthenticated(
                {"message": "Could Not Authenticate User",
                 "status_code":
                 status.HTTP_401_UNAUTHORIZED})
        elif len(auth_header) > 2:
            '''
            More parmeters have been passed
            '''
            raise exceptions.NotAuthenticated(
                {"message":
                 "Could Not Authenticate,Invalid Values Passed",
                 "status_code": status.HTTP_401_UNAUTHORIZED})
        try:

            prefix = auth_header[0]
            token = auth_header[1]
        except Exception:
            raise exceptions.NotAcceptable(
                {"message": "No Token Present",
                 "status_code":
                 status.HTTP_406_NOT_ACCEPTABLE})
        if prefix.lower() != auth_header_prefix:
            return None
        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        try:
            payload = jwt.decode(token, C.TOKEN_SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                {"message":
                 "User Logged Out.Please Try Again",
                 "status_code":
                 status.HTTP_401_UNAUTHORIZED})

        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed(
                {"message": "Please Try Logging In Again",
                 "status_code":
                 status.HTTP_401_UNAUTHORIZED})

        except Exception as e:
            print(e)
            raise exceptions.AuthenticationFailed(
                {"message":
                 "Invalid Verification",
                 "status_code": status.HTTP_401_UNAUTHORIZED})

        try:
            user = User.objects.get(id=payload['user'])
        except User.DoesNotExist:

            raise exceptions.AuthenticationFailed(
                {"message": "Invalid User",
                 "status_code":
                 status.HTTP_401_UNAUTHORIZED})
        return (user, token)
