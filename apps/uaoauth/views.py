from django.contrib.auth import get_user_model
from requests import post as req_post
from requests import exceptions
from rest_auth.serializers import TokenSerializer
from rest_framework import serializers
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .settings import *


class UAOauthSerializer(serializers.Serializer):
    lastname = serializers.CharField()
    middlename = serializers.CharField(required=False, allow_blank=True)
    givenname = serializers.CharField()
    edrpoucode = serializers.CharField(required=False, allow_blank=True)
    drfocode = serializers.CharField(required=False, allow_blank=True)


class BearesSerializer(serializers.Serializer):
    code = serializers.CharField()
    state = serializers.CharField()


class UserUAoauthSerializer(serializers.Serializer):
    """{
    "access_token": "2c71170938c539f628b9a187ef776061e5431979",
    "token_type": "bearer",
    "expires_in": 1596225158,
    "refresh_token": "cc4b144cccd033594104ead46f1ab1aaa127787a",
    "user_id": "4270986"
}"""
    access_token = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()
    refresh_token = serializers.CharField()
    user_id = serializers.CharField()


class UAOauthLoginView(APIView):
    permission_classes = (AllowAny,)
    token_model = Token
    token_serializer_class = TokenSerializer
    UserModel = get_user_model()

    def post(self, request, *args, **kwargs):
        self.request = request
        code_data = self.get_acess_token(request)
        user_data = self.get_user_data(code_data)
        self.login(user_data)
        return self.get_response()

    def get_acess_token(self, request):
        print('get_acess_token')
        serializer = BearesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ##self.redirect_uri = serializer.validated_data['redirect_uri'],
        data = {"grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": serializer.validated_data['code'],
                ##"redirect_uri": self.redirect_uri
                }
        try:
            res = req_post(ACCESS_TOKEN_URL, data=data)
        except exceptions.ConnectionError as e:
            raise ValidationError({
                'non_field_errors': 'Не вдалось підєднатись до серверу автоизації',
                'details':str(e)})
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 401:
            raise ValidationError(res.json())

    def get_user_data(self, code_data):
        print('get_user_data')
        print(code_data)
        serializer = UserUAoauthSerializer(data=code_data)
        serializer.is_valid(raise_exception=True)

        data = {"access_token": serializer.validated_data['access_token'],
                "user_id": serializer.validated_data['user_id']
                }
        res = req_post(USER_INFO_URL, data=data)
        print(USER_INFO_URL+'?='+"access_token="+serializer.validated_data['access_token']+'&'"user_id="+ serializer.validated_data['user_id'])
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 401:
            raise ValidationError(res.json())

    def get_user(self, data):
        print('get_user')
        ##Отрмуємо користувача з ІПН, якщо існує - повертаємо користувача
        user_q = self.UserModel.objects.filter(ipn=data['drfocode'])

        if user_q.exists():
            return user_q.first()
        ##Якщо не вдалось знайти користувача за ІПН, знаходимо по прівжу та імені
        user_q2 = self.UserModel.objects.filter(first_name__iexact=data['givenname'],
                                                last_name__iexact=data['lastname'], )
        if user_q2.exists():
            if user_q2.count() > 1:
                raise ValidationError(
                    {
                        'non_field_errors': f'User with params givenname={data["givenname"]}, last_name={data["lastname"]}, more then one person.You can\'t login by this params'})

            return user_q2.first()

        raise ValidationError({'non_field_errors': f'User not register in system'})

    def get_response(self):
        response = Response(self.token_serializer.data, status=status.HTTP_200_OK)
        return response

    def login(self, data):
        print('login')
        print(data)
        serializer = UAOauthSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.user = self.get_user(serializer.validated_data)
        token, _ = self.token_model.objects.get_or_create(user=self.user)
        self.token_serializer = self.token_serializer_class(instance=token,
                                                            context={'request': self.request})
