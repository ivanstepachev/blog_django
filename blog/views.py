from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.db.models import Count

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm

from taggit.models import Tag

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    # задаем кастомное имя для контекста, default = object_list
    paginate_by = 3
    # пагинация объектов по три штуки
    # в шаблоне при покдлючении пагинации page=page_obj
    template_name = 'blog/post/list.html'


# аналогичен верхнему варианту
def post_list(request, tag_slug=None):
    # эта вью может обрабатывать два урл с tag_slug и без
    object_list = Post.published.all()
    # так как queryset ленивый можно не передивать что мы дважды вытаскиваем список объектов (ниже в условиях если тэг),
    # так как он будет выполненен только при рендеринге страницы
    tag = None
    if tag_slug:
        # если tag_slug есть в урл
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
        # tag предаем списоком, чтобы фильтр __in сработал и так как между Post и Tag Many-to-Many
    paginator = Paginator(object_list, 3)
    # создает последовательность Pages с заданным количеством объектов списка те 3 штуки
    # те создавая пагинатор мы получаем возможность в гет запросе получать 'page' значение,
    # так как он есть на всех страницах потому что мы включаем его через include на все страницы
    page = request.GET.get('page')
    # это объект класса Page, page это список объектов на странице
    try:
        posts = paginator.page(page)
        # в шаблоне при покдлючении пагинации page=posts
        # получаем объекты для заданной страницы
    except EmptyPage:
        posts = paginator.page(1)
    except PageNotAnInteger:
        posts = paginator.page(paginator.num_pages)
        # эта ошибка обрабатывает первую загрузку, то есть когда страница еще не может быть обработана
        # возвращает последнюю страницу,
        # т к paginator.num_pages возвращает общее количество страниц
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    # get_object_or_404 так же может фильтровать объект по многим параметрам
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day
                             )
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            # создаем объект комментария без сохранения в БД
            # метод save() можно приенять к формам от ModelForm, просто Form обрабатываются вручную
            new_comment.post = post
            # задаем объекту комеентария поле post
            new_comment.save()
            # и сохраняем в БД
            # редирект отсутвует, происходт перезагрузка на эту же страницу с добавденным комментарием
    else:
        comment_form = CommentForm()
    post_tags_ids = post.tags.values_list('id', flat=True)
    # реккомендация схожих постов по тегу
    # values_list получает QS кортежей объектов с указанными полями, flat=True говорит что если кортеж состоит из
    # одного значения, то иы получаем QS со сзначениями указанного поля. Например <QS[1, 2, 3 ...]>
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    # ищем посты с этими тегами, исключая пост в котором мы находимся tags__id__in аналогична tags__in
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    # так как фильтрация идет перед анотацией, поэтому она влияет на нее, и сохранились только общие тэги
    # и это позволяет нам их посчитать(общие)-
    # фильтрация имеет эффект ограничения объектов для которой расчитывается анатоцация
    # фильтруем по большинству совпадений тэгов в посте и делаем максимально 4 рекомендации
    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'new_comment': new_comment,
                                                     'comment_form': comment_form,
                                                     'similar_posts': similar_posts})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    # используем в шаблоне для алерта для успешной отправки
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        # else обрабатывается автоматически и если неверна то страница перезагружается
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            # строим полный урл адрес, включая хттп доменное имя и поля с помощью build_absolute_url
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            # функция для отправки письма (заголовок, сообщение, от кого, список получателей)
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    # query это название поля в форме, то есть проверяем есть ли запрос в форме
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        # GET запрос так же проверяем на валидность
        if form.is_valid():
            query = form.cleaned_data['query']
            # проводим поиск по заголовку и телу поста
            # имя аргумента в аннотации и в фильтре должны быть одинаковыми, вариант 1
            # results = Post.published.annotate(search=SearchVector('title', 'body'),).filter(search=query)

            # в данном примере мы с помощью SearchQuery(кот-ый имет спец алгоритмы)
            # находим совпадение запросов по корню слов.
            # с помощью SearchRank делаем более эффективную ранжировку совпадений
            # search_vector = SearchVector('title', 'body')
            # search_query = SearchQuery(query)
            # results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)
            #                                   ).filter(search=search_query).order_by('-rank')

            # в данном случае с помощью аргумента weight мы определяем где важнее искать соответсвие
            # в какой Search Vector, то есть таблице, в даннои случае фильтр настроен на rank более 0.3
            # D=0.1, C=0.2, B=0.4, A=1.0
            # search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            # search_query = SearchQuery(query)
            # results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)
            #                                   ).filter(rank__gte=0.3).order_by('-rank')

            # Поиск на основе триграм, то есть трех послеловательных букв с двух строках и считает совпадения
            # Так как во многих языках слова совпадают, это являетя эффективным поиском
            # Для этого в postgres нужно установить pg_trgm
            results = Post.published.annotate(similarity=TrigramSimilarity('title', query),).filter(similarity__gt=0.1).order_by('-similarity')
    return render(request, 'blog/post/search.html', {'form': form,
                                                     'query': query,
                                                     'results': results})
