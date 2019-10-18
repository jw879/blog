from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import markdown
from django.utils.html import strip_tags


# Create your models here.

# Django 内置数据库，可以直接写数据表

class Category(models.Model):  # Django 规定模型必须继承models.Model类
    name = models.CharField(max_length=100)  # Charfield 指定类名的数据类型（字符型）

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField('标题', max_length=70)
    body = models.TextField('正文')  # 正文使用Textfield来储存大段文本!!

    #  这两个列表表示文章创建时间和最后一次修改时间：
    created_time = models.DateTimeField('创建时间', default=timezone.now)
    modified_time = models.DateTimeField('修改时间')

    #  文章摘要，值可以为空
    excerpt = models.CharField('摘要', max_length=200, blank=True)

    # CASCADE表示级联删除，意思是删除一个分类，则该分类下所有电影都被删除
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE)
    #  标签与电影是多对多的关系
    tags = models.ManyToManyField(Tag, verbose_name='标签', blank=True)

    author = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.modified_time = timezone.now()

        # 首先实例化一个 Markdown 类，用于渲染 body 的文本。
        # 由于摘要并不需要生成文章目录，所以去掉了目录拓展。
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
        ])

        # 先将 Markdown 文本渲染成 HTML 文本
        # strip_tags 去掉 HTML 文本的全部 HTML 标签
        # 从文本摘取前 54 个字符赋给 excerpt
        self.excerpt = strip_tags(md.convert(self.body))[:54]

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title
