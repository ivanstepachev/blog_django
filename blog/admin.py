from django.contrib import admin

from .models import Post, Comment


# Декоратор для регистрация класса в админке
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    # list_display отображение созданных объектов в админке в виде списка с заданными столбцами
    list_filter = ('status', 'created', 'publish', 'author')
    # list_filter Добавляет столбец с фильтрами по указанным полям
    search_fields = ('title', 'body')
    # search_fields добавляет поисковую строку для объектов по указанным полям
    prepopulated_fields = {'slug': ('title',)}
    # prepopulated_fields во время создания объекта при задании title, автоматически заполняется slug,
    # совпадая с title
    raw_id_fields = ('author',)
    # raw_id_fields при создании объекта, поле автора задается через поисковик по имени,
    # а не вываливающийся список. Удобно когда много значений
    date_hierarchy = 'publish'
    # date_hierarchy добавляет вкладку фильтр с датами
    ordering = ('status', 'publish')
    # ordering добаялет в указанных поляъ возможность сортировки по возрастанию.убыванию


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')
