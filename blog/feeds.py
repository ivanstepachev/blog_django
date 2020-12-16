# Создание xml файлов для RSS подписок, используя Syndication feed framework
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from django.urls import reverse_lazy
from .models import Post


class LatestPostFeed(Feed):
    # заголвок, ссылка, описание rss элементов, так как это класс используем reverse_lazy для построения URL
    title = 'My blog'
    link = reverse_lazy('blog:post_list')
    description = 'New posts of my blog.'

    # объекты включенные в feed
    def items(self):
        return Post.published.all()[:5]

    # получаем заголовок каждого поста
    def item_title(self, item):
        return item.title

    # описание на 30 словБ исользум для этого метод шаблонного фильтра!
    def item_description(self, item):
        return truncatewords(item.body, 30)
