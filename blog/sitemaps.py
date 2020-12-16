from django.contrib.sitemaps import Sitemap
from .models import Post


# создаем кастомный sitemap, наследуя Sitemap class
# changefreq частота изменения страниц постов, priority актуальность
class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    # список объектов для включения их в sitemap
    # так как мы задали get_absolute_url для постов.
    def items(self):
        return Post.published.all()

    # возвращает время последнего изменения объектов, полученных из items()
    def lastmod(self, obj):
        return obj.updated