from django.urls import path
from . import views
from .feeds import LatestPostFeed

# определяем пространство имен, для текущего приложения, чтобы в шаблоне образаться blog:post_list и т д
app_name = 'blog'
urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>',
         views.post_detail, name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    # этот урл обрабатывается одним и тем же view с первым варинтом, вью обрабатывает наличия tag_slug
    path('feed/', LatestPostFeed(), name='post_feed'),
    # для RSS feed
    path('search/', views.post_search, name='post_search'),
]
# <slug:post> гворит о том, что эта часть урл может состоять из букв или дефисов
# path имеет встроенный конвертор, который из строки делает нужные значения типа int, slug и т д
# создание отдельно урд для каждого приложения делает возможным, чтобы это
# приложение могли комфортно использовать другие

