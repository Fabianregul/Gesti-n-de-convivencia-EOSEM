from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_login, name='login'),
    path('logout/', views.view_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reportes/', views.ver_reportes, name='reportes'),
    path('estudiante/guardar/', views.guardar_estudiante, name='guardar_estudiante'),
    path('estudiante/editar/<int:id>/', views.editar_estudiante, name='editar_estudiante'),
    path('estudiante/eliminar/<int:id>/', views.eliminar_estudiante, name='eliminar_estudiante'),
    path('reporte/guardar/', views.guardar_reporte, name='guardar_reporte'),
    path('estudiante/eliminar/<int:id>/', views.eliminar_estudiante, name='eliminar_estudiante'),
    path('descargar-reporte/', views.descargar_pdf, name='descargar_pdf'),
]