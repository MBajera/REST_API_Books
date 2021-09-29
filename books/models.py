from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=512, unique=True)

    def __str__(self):
        return self.name


class Categories(models.Model):
    name = models.CharField(max_length=512, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=512)
    authors = models.ManyToManyField(Author)
    published_date = models.IntegerField(null=True)
    categories = models.ManyToManyField(Categories)
    average_rating = models.FloatField(null=True)
    ratings_count = models.IntegerField(null=True)
    thumbnail = models.CharField(max_length=512, null=True)