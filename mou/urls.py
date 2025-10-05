from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_mou, name='create_mou'),
    path('', views.mou_list, name='mou_list'),
    path('mou/<int:mou_id>/add_event/', views.add_event, name='add_event'),
    path('view/<int:mou_id>/', views.view_mou, name='view_mou'),
    path('edit/<int:mou_id>/', views.edit_mou, name='edit_mou'),
    path('delete/<int:mou_id>/', views.delete_mou, name='delete_mou'),
    path('event/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('filter/', views.filter_mou, name='filter_mou'),
    path('about/', views.about, name='about'),
    path('home',  views.mou_list, name='mou_list'),
    path('show-database/', views.show_database, name='show_database'),
    path('student/', views.student, name='student'),
    path('company/', views.company, name='company'),
    path('student_view/<int:mou_id>/', views.student_view, name='student_view')
    ,
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('mou/<int:mou_id>/report/pdf/', views.mou_report_pdf, name='mou_report_pdf'),
    path('mou/<int:mou_id>/report/email/', views.send_mou_report_email, name='send_mou_report_email'),
]