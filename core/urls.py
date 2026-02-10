from django.urls import path
from .views import download_pdf
from .views import dashboard, monthly_report
from .views import monthly_excel, delete_entry, edit_entry
from .views import entry_list

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('download-pdf/', download_pdf, name='download_pdf'),
    path('monthly/', monthly_report, name='monthly_report'),
    path('monthly-excel/', monthly_excel, name='monthly_excel'),
    path('delete/<int:entry_id>/', delete_entry, name='delete_entry'),
    path('edit/<int:entry_id>/', edit_entry, name='edit_entry'),
    path('api/entries/', entry_list),

]
