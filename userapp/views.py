from django.shortcuts import render
from .serializers import CustomerSerializer, CustomerProfileSerializer,ResetPasswordSerializer
from .models import Customer,PasswordResetOtp
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import IsAuthenticated
import  random
from django.core.mail import send_mail
from userapp.tasks import send_otp_email,send_registration_email

from specspotProject.settings import EMAIL_HOST_USER
from rest_framework.permissions import AllowAny
from rest_framework import status, serializers,generics

# Create your views here.


class CreateCustomerView(APIView):
    def post(self, request):
        user = CustomerSerializer(data=request.data)
        if user.is_valid():
            instance = user.save()

            send_registration_email.delay(instance.email,instance.name)

            # subject = "Welcome to our site"
            # message = (
            #     f"Hello {instance.name},\n\n"
            #     f"Thank you for registering with us!\n"
            #     f"Happy shopping!"
            # )
            # recipient_list = [instance.email]

            # send_mail(
            #     subject,
            #     message,
            #     EMAIL_HOST_USER,  # same as your Django example
            #     recipient_list,
            #     fail_silently=False
            # )
            return Response(user.data, status=status.HTTP_201_CREATED)
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        users = Customer.objects.all()
        serializer = CustomerSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoginCustomerView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'error': 'please give email and password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response({'error': 'invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response(
                {"error": "Your account has been blocked by admin."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if user:

            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh)
            access_token = str(refresh.access_token)

            user_data = CustomerProfileSerializer(user).data

            response = Response({
                "data": "login successful;",
                "user": user_data,
                "access_token": access_token
            }, status=status.HTTP_202_ACCEPTED)

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="None",
                path="/"

            )
            return response
        return Response({'detail': 'invalid credential'}, status=status.HTTP_403_FORBIDDEN)

# token refresh view for automatically creating access token


class CookieTokenRefreshView(APIView):

    permission_classes = [AllowAny]  # Allow access even if Access Token is expired
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        print('refresh_token',refresh_token)
        if not refresh_token:
            return Response({'error':'refresh token missing'},status=400)
        
        print('refresh_token',refresh_token)

        try:
            token = RefreshToken(refresh_token)
            user_id = token['user_id']
            user = Customer.objects.get(id=user_id)
            new_refresh = RefreshToken.for_user(user)
            new_access = new_refresh.access_token
            token.blacklist()
        except Exception as e:
      
            return Response({"detail": "Invalid or expired refresh token"}, status=401)
        
        response = Response({
            'message':'token refreshed successfully',
            'access_token':str(new_access)
        })
        response.set_cookie(
            "refresh_token",
            str(new_refresh),
            httponly=True,
            secure=True,
            samesite='None',
            path='/'
        )

        return response
        # above can also be written like this.

        # if serializer.is_valid():
        #     return Response(serializer.validated_data, status=200)
        # else:
        #     return Response({"error": "Invalid refresh token"},status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        response = Response({'message': "logout successful"},
                            status=status.HTTP_200_OK)

        response.delete_cookie(
            key="refresh_token",
            samesite="None",
        )
        return response

class CustomerProfileView(generics.RetrieveAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=CustomerProfileSerializer
    def get_object(self):
        return self.request.user
    
# reset password generate otp view 

class GenerateOTP(APIView):
    def post(self,request):
        email = request.data.get('email')

        if not email:
            return Response({'error':'you must give email'},status=status.HTTP_400_BAD_REQUEST)
        try:
            user = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return Response({'error':'the given email is not a valid one'},status=status.HTTP_400_BAD_REQUEST)
        
        otp = str(random.randint(100000,999999))
        session = PasswordResetOtp.objects.create(user=user,otp=otp)


        # subject = "Your requested password request otp  "
        # message = (
        #     f"Hello {email},\n\n"
        #     f"OTP:{otp}\n"
        # )
        # recipient_list = [email]

        # send_mail(
        #     subject,
        #     message,
        #     EMAIL_HOST_USER,  # same as your Django example
        #     recipient_list,
        #     fail_silently=False
        # )
        # print(f"Otp {otp}")

        send_otp_email.delay(email,otp)
        print(f"Otp {otp}")


        return Response({

            "message": "OTP has been sent to your email.",
            "reset_session":session.reset_session
        },status=status.HTTP_200_OK)
    
class VerifyOtp(APIView):
    def post(self,request):
        reset_session = request.data.get('reset_session')
        entered_otp = request.data.get('otp')

        if not entered_otp or not reset_session:
            return Response({'error':'please enter the otp! and also reset_session required!'},status=status.HTTP_400_BAD_REQUEST)
        try:
            otp_obj = PasswordResetOtp.objects.get(reset_session=reset_session)
        except PasswordResetOtp.DoesNotExist:
            return Response({'error':'invalid session'},status=status.HTTP_400_BAD_REQUEST)

        if otp_obj.is_expired():
            return Response({'error':'otp expired!'},status=status.HTTP_400_BAD_REQUEST)
        if otp_obj.otp != entered_otp:
            return Response({'error':'the otps did not match'},status=status.HTTP_400_BAD_REQUEST)
        
        otp_obj.is_verified=True
        otp_obj.save()
        return Response({'message':'otp verified'},status=status.HTTP_200_OK)

# class ResetPassword(APIView):
#     def post(self,request): 
#         reset_session = request.data.get('reset_session')
#         new_password = request.data.get('password')

#         try:
#             otp_obj = PasswordResetOtp.objects.get(reset_session=reset_session,is_verified = True)
#         except:
#             return Response({'error':'Invalid session'},status=status.HTTP_400_BAD_REQUEST)
        
#         user =otp_obj.user
#         user.set_password(new_password)
#         user.save()

#         otp_obj.delete()
#         return Response({'message':'password changed successfully!'},status=status.HTTP_200_OK)

class ResetPassword(APIView):
    def post(self,request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_session = serializer.validated_data['reset_session']
        password = serializer.validated_data['password']

        try:
            otp_obj = PasswordResetOtp.objects.get(
                reset_session=reset_session,
                is_verified=True
            )
        except PasswordResetOtp.DoesNotExist:
            return Response(
                {"error": "Invalid session"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = otp_obj.user
        user.set_password(password)
        user.save()

        otp_obj.delete()

        return Response(
            {"message": "Password changed successfully!"},
            status=status.HTTP_200_OK
        )