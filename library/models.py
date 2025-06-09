from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

class Author(models.Model):
   first_name = models.CharField(max_length=100)
   last_name = models.CharField(max_length=100)
   date_of_birth = models.DateField(null=True, blank=True)
   profile = models.URLField(null=True, blank=True, verbose_name="Author profile URL")
   deleted = models.BooleanField(default=False, help_text="Is author deleted?")
   rating = models.IntegerField(
       null=True,
       blank=True,
       default=1,
       validators=[MinValueValidator(1), MaxValueValidator(10)]
   )

   def __str__(self):
       return f"{self.first_name} {self.last_name}"


GENRE_CHOICES = {
    'FICTION': 'Fiction',
    'NON_FICTION': 'Non-Fiction',
    'SCI_FI': 'Science Fiction',
    'FANTASY': 'Fantasy',
    'MYSTERY': 'Mystery',
    'BIOGRAPHY': 'Biography',
    'NOT_SET': 'Not Set',
}


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    publication_date = models.DateField()
    description = models.TextField(null=True, blank=True)
    genre = models.CharField(choices=GENRE_CHOICES, default='NOT_SET')
    amount_of_pages = models.PositiveIntegerField(validators=[MaxValueValidator(10_000)], default=20)

    publisher = models.ForeignKey("Publisher", on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey("Category", null=True, on_delete=models.SET_NULL, related_name='books')
    libraries = models.ManyToManyField("Library", related_name='books')
    # publisher_id = models.ForeignKey("Member", null=True, on_delete=models.CASCADE)



    def __str__(self):
        return self.title



class Publisher(models.Model):
    name = models.CharField(max_length=100)
    adress = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100)


    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Library(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    site = models.URLField(null=True, blank=True, verbose_name="Library URL")

    def __str__(self):
        return self.name


GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
]

ROLE_CHOICES = [('A', 'Administrator'),
                ('R', 'Reader'),
                ('E','Employe'),]


class Member(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES)
    birth_date = models.DateField()
    age = models.PositiveIntegerField(verbose_name="Age", editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    active = models.BooleanField(default=True)
    libraries = models.ManyToManyField('Library', related_name='members')

    def save(self, *args, **kwargs):
        ages = timezone.now().year - self.birth_date.year
        if 6 < ages < 120:
            self.age = ages
            super().save(*args, **kwargs)
        else:
            raise ValidationError("Age must be between 6 and 120")


    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Posts(models.Model):
    title = models.CharField(max_length=255, unique_for_date='created_at')
    body = models.TextField()
    author = models.ForeignKey(Member, on_delete=models.CASCADE,
                               related_name='posts')
    moderated = models.BooleanField(default=False)
    library = models.ForeignKey(Library, on_delete=models.CASCADE,
                                related_name='posts')
    created_at = models.DateField()
    updated_at = models.DateField(auto_now=True)


class Borrow(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE,
                               related_name='borrows')
    book = models.ForeignKey(Book, on_delete=models.CASCADE,
                             related_name='borrows')
    library = models.ForeignKey(Library, on_delete=models.CASCADE,
                                related_name='borrows')
    borrow_date = models.DateField()
    return_date = models.DateField()
    returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.member.first_name} {self.member.last_name}"

    def is_overdue(self):
        if self.returned:
            return False
        return self.return_date < timezone.now().date()