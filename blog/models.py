from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager


# Создаем кастомный менеджер моделей, вместо Model.objects
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):

    # draft - значение, Draft отображение в форме
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    # Slug (по другому часть URL адреса), используется в моделях для генерации уникального URL для объекта
    # unique_for_date строим URL с помощью publish date и slug,
    # то есть в определенную дату публикации может быть только один уникальный sluf
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    # auto_now_add Дата и время создается при создании объекта
    updated = models.DateTimeField(auto_now=True)
    # auto_now Дата и время добавляется, когда объект сохраняется
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    # choices принимает список с вариантами выбора для текстового поля
    objects = models.Manager()
    # дефолтный менеджер моделей, если мы не задаем дефолтный , то он добавляется автоматисески к каждой модели
    # так как мы добавили кастомный, надо добавить дефолтный чтобы он сохранил свое действие
    published = PublishedManager()
    # наш кастомный менеджер и можем обращаться Post.published.filter(...) фильтрует по уже опубликованным постам
    tags = TaggableManager()
    # систеиа тегов через taggit

    # ordering упорядовачивание объектов при запросе в БД, минус означает что в обратном порядке
    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    # метод который возвращает "канонический" урл для модели,
    # используется в шаблонах для обращения к определенному посту, удобно для ссылок сложных
    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[
            self.publish.year,
            self.publish.month,
            self.publish.day,
            self.slug
        ])
    # reverse создает url


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"
