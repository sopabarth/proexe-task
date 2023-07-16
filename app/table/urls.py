from django.urls import path
from . import views

urlpatterns = [
    path('', views.generate_dynamic_model),
    path('<str:id>', views.update_dynamic_model),
    path('<str:id>/row', views.add_row),
    path('<str:id>/rows', views.list_rows)
]
