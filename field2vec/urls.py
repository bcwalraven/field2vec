from django.contrib import admin
from django.urls import path

from field2vec.views.vector import add_vector

urlpatterns = [
    path('admin/', admin.site.urls),
    path('add_vector/', add_vector),
]
