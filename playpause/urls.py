from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'pause_count_distribution', views.pause_count_distribution, name='pause_count_distribution')
]
