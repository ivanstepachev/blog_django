from django import template
from django.db.models import Count
from ..models import Post
from django.utils.safestring import mark_safe
import markdown


# создаем собственный template tag
# первым делом надо определить переменную register, чтобы новый тэг был валидным
register = template.Library()


# добавляем декоратор, тэг будет называться как функция,
# либо можно задать имя по-другому(@register.simple_tag(name='foo_name')
# чтобы тег работал надо перезагрузить сервер
@register.simple_tag
def total_posts():
    return Post.published.count()


# inclusion tag возвращает срендеренную страницу, simple строковое представление простого значения в html
# находятся в base.html
@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


# самый комментируемый пост через аннотацию, как аналогия к прошлому примеру только через simple_tag
@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]


# mark_safe помечает строку как безопасную для вывода в html
# создаем фильтр для конвертации markdown в html
@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
