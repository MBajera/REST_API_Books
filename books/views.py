from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import Book, Categories, Author
from .serializers import BookSerializer, BookImportSerializer
from django.views import View
from django.shortcuts import render


class HomeView(View):
    def get(self, request):
        return render(request, "base.html")


class BooksListView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = Book.objects.all()
        published_date = self.request.query_params.get('published_date')
        if published_date is not None:
            queryset = queryset.filter(published_date=published_date)
        sort = self.request.query_params.get('sort')
        if sort is not None:
            queryset = queryset.order_by(sort)
        author = self.request.query_params.getlist('author')
        if author is not None and len(author) > 0:
            queryset = queryset.filter(authors__in=[Author.objects.get(name=elem) for elem in author])
        return queryset


class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


def get_dict_data(resp_dict):
    average_rating = resp_dict['volumeInfo'].get('averageRating')
    if average_rating is not None:
        average_rating = float(average_rating)
    ratings_count = resp_dict['volumeInfo'].get('ratingsCount')
    if ratings_count is not None:
        ratings_count = float(ratings_count)
    if resp_dict['volumeInfo'].get('authors') is not None:
        authors = [elem for elem in resp_dict['volumeInfo']['authors']]
    else:
        authors = None
    if resp_dict['volumeInfo'].get('categories') is not None:
        categories = [elem for elem in resp_dict['volumeInfo']['categories']]
    else:
        categories = None
    published_date = resp_dict['volumeInfo']['publishedDate']
    if len(published_date) > 4:
        published_date = published_date[:4]
    thumbnail = resp_dict['volumeInfo'].get('imageLinks')
    if thumbnail is not None:
        thumbnail = resp_dict['volumeInfo']['imageLinks'].get('thumbnail')
    new_dict = {
        'slug': resp_dict['id'],
        'title': resp_dict['volumeInfo']['title'],
        'published_date': int(published_date),
        'average_rating': average_rating,
        'ratings_count': ratings_count,
        'thumbnail': thumbnail,
        'authors': authors,
        'categories': categories
    }
    return new_dict


def set_authors_and_categories(authors, categories, book):
    if authors is not None:
        for elem in authors:
            obj, created = Author.objects.get_or_create(name=elem)
            book.authors.add(obj)
    if categories is not None:
        for elem in categories:
            obj, created = Categories.objects.get_or_create(name=elem)
            book.categories.add(obj)


class BookImportView(APIView):
    def post(self, request):
        serializer = BookImportSerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.data['q']
            url = f'https://www.googleapis.com/books/v1/volumes?q={query}'
            response = requests.get(url)
            if response.json()['totalItems'] < 1:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            data = response.json()['items']
            for item in data:
                item_data = get_dict_data(item)
                if Book.objects.filter(slug=item_data['slug']):
                    book = Book.objects.get(slug=item_data['slug'])
                    book.slug = item_data['slug']
                    book.title = item_data['title']
                    book.published_date = item_data['published_date']
                    book.average_rating = item_data['average_rating']
                    book.ratings_count = item_data['ratings_count']
                    book.thumbnail = item_data['thumbnail']
                    book.authors.clear()
                    book.categories.clear()
                    set_authors_and_categories(item_data['authors'], item_data['categories'], book)
                    book.save()
                else:
                    book = Book.objects.create(
                        slug=item_data['slug'],
                        title=item_data['title'],
                        published_date=item_data['published_date'],
                        average_rating=item_data['average_rating'],
                        ratings_count=item_data['ratings_count'],
                        thumbnail=item_data['thumbnail']
                    )
                    set_authors_and_categories(item_data['authors'], item_data['categories'], book)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)