from django.urls import path
from .views import ProductVariantView, ProductsView, CategoriesView

urlpatterns = [
    path("categories/", view=CategoriesView.as_view()),
    path("add-category/", view=CategoriesView.as_view()),
    path("edit-category/", view=CategoriesView.as_view()),
    path("categories/<uuid:pk>/", view=CategoriesView.as_view()),
    path("products/", view=ProductsView.as_view()),
    path("add-product/", view=ProductsView.as_view()),
    path("get-product-variants/", view=ProductVariantView.as_view()),
    path("add-product-variant/", view=ProductVariantView.as_view()),
    path("products/<uuid:pk>/", view=ProductsView.as_view()),
]
