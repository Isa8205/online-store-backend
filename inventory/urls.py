from django.urls import path
from .views import ProductsView, CategoriesView

urlpatterns = [
    path("categories/", view=CategoriesView.as_view()),
    path("add-category/", view=CategoriesView.as_view()),
    path("edit-category/", view=CategoriesView.as_view()),
    path("categories/<int:pk>/", view=CategoriesView.as_view()),
    path("products/", view=ProductsView.as_view()),
    path("add-product/", view=ProductsView.as_view()),
    path("products/<int:pk>/", view=ProductsView.as_view()),
]
