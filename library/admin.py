from django.contrib import admin
from library.models import Author, Book, Publisher, Category, Library, Member, Posts, Borrow

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Publisher)
admin.site.register(Category)
admin.site.register(Library)
admin.site.register(Member)
admin.site.register(Posts)
admin.site.register(Borrow)

