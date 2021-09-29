from rest_framework import serializers
from .models import Book, Author, Categories


class BookSerializer(serializers.ModelSerializer):
    authors = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Author.objects.all())
    categories = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Categories.objects.all())

    class Meta:
        model = Book
        fields = ('title', 'authors', 'published_date', 'categories', 'average_rating', 'ratings_count', 'thumbnail')


class BookImportSerializer(serializers.Serializer):
    q = serializers.CharField(max_length=256)