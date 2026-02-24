from django.shortcuts import render
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category, Product, ProductImage
from .serializers import CategorySerializer, ProductSerializer, ProductAddSerializer
from rest_framework import status

# Create your views here.
class ProductsView(APIView):    
    def get(self, request):
        products = Product.objects.select_related('category').all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        print(request.data)
        serializer = ProductAddSerializer(data=request.data)

        if serializer.is_valid():

            with transaction.atomic():
                serializer.save()

            return Response({"message": "The data was received and saved on the server!"}, status=status.HTTP_201_CREATED)
        
        print(f"Errors occured: {serializer.errors}")
        return Response({"Message": "Encountered an error. Please try again."}, status=status.HTTP_400_BAD_REQUEST)
        
class CategoriesView(APIView):    
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            name = serializer.validated_data.get("name")
            
            if name:
                category_exists = Category.objects.filter(name=name).exists()

                if not category_exists:    
                    serializer.save()
                    return Response({"message": "Category saved successfully"}, status=status.HTTP_201_CREATED)
                
                return Response({"message": "Category already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Errors occured: {serializer.errors}")
        return Response({"Message": "Encountered an error. Please try again."}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            name = serializer.validated_data.get("name")
            description = serializer.validated_data.get("description")
            
            if name:
                category = Category.objects.filter(name=name).first()

                if category:
                    category.name = name
                    category.description = description
                    category.save()
                    return Response({"message": "Changes saved successfully"}, status=status.HTTP_202_ACCEPTED)
                
                return Response({"message": "Category does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Errors occured: {serializer.errors}")
        return Response({"Message": "Encountered an error. Please try again."}, status=status.HTTP_400_BAD_REQUEST)
