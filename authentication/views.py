from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from datetime import datetime

from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer
from config import settings

User = get_user_model()

class MeView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request):
        return Response(UserSerializer(request.user, context={"request": request}).data)
    
class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'No refresh token found'}, status=status.HTTP_401_UNAUTHORIZED)

        # Inject into request.data so parent can handle it
        request.data['refresh'] = refresh_token

        try:
            response = super().post(request, *args, **kwargs)

            # The parent returns Response({'access': 'token_here'})
            access_token = response.data.get('access')

            # Set HttpOnly cookie
            token_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
            res = Response({'detail': 'Token refreshed'})
            res.set_cookie(
                'access_token',
                access_token,
                httponly=True,
                secure=True,
                samesite='None',
                max_age=int(token_lifetime)
            )
            return res

        except TokenError as e:
            raise InvalidToken(e.args[0])


 
class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        login_serializer = UserLoginSerializer(data=request.data)

        if login_serializer.is_valid(raise_exception=True):
            username_or_email = login_serializer.validated_data['username_or_email']
            password = login_serializer.validated_data['password']

            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    username = user_obj.username
                except User.DoesNotExist:
                    return Response({'message': "Failed! Check credentials and try again."}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                username = username_or_email

            user = authenticate(request, username=username, password=password)

            if user:
                user_serializer = UserSerializer(user, context={"request": request})
                refresh = RefreshToken.for_user(user)

                response =  Response({
                    "user": user_serializer.data,
                    "message": "Login successful"
                    }, 
                    status=status.HTTP_200_OK)

                access_exiration = datetime.now() + refresh.access_token.lifetime
                response.set_cookie(
                    key='access_token',
                    expires=access_exiration,
                    value=str(refresh.access_token),
                    httponly=True,
                    secure=True, # Set to True in production with HTTPS
                    samesite='None' # Adjust based on your requirements
                )

                refresh_expiration = datetime.now() + refresh.lifetime
                response.set_cookie(
                    key='refresh_token', 
                    expires=refresh_expiration,
                    value=str(refresh),
                    httponly=True,
                    secure=True, # Set to True in production with HTTPS
                    samesite='None' # Adjust based on your requirements
                )

                return response
            
        print(f"Errors occured: {login_serializer.errors}")
        return Response({'message': "Failed! Check credentials and try again."}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response({"Message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        response = Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
