from django.db import models

from django_immediate_fk import ForeignKeyConstraint


class Author(models.Model):
    name = models.CharField()


class Book(models.Model):
    title = models.CharField()
    author = models.ForeignKey(Author, on_delete=models.DB_CASCADE, db_constraint=False)

    class Meta:
        constraints = [
            ForeignKeyConstraint(name="books_book_author_immediate", field="author"),
        ]
