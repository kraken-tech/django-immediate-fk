import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.constraints import UniqueConstraint
from django_subatomic import db

from .books.models import Author, Book
from django_immediate_fk import ImmediateDeferrableFKConstraint


@pytest.mark.django_db(transaction=True)
def test_immediate_foreign_key_integrity_error():
    with db.transaction():
        with pytest.raises(IntegrityError):
            Book.objects.create(author_id=-1)


@pytest.mark.django_db
def test_immediate_foreign_key_full_clean():
    tolkien = Author.objects.create(name="Tolkien")
    hobbit = Book.objects.create(title="The Hobbit", author=tolkien)
    hobbit.author_id = -1

    with db.transaction():
        with pytest.raises(ValidationError):
            hobbit.full_clean()


def test_eq():
    constraint = ImmediateDeferrableFKConstraint(name="name", field="author")
    assert constraint == ImmediateDeferrableFKConstraint(name="name", field="author")
    assert constraint != ImmediateDeferrableFKConstraint(name="other", field="author")
    assert constraint != ImmediateDeferrableFKConstraint(name="name", field="other")
    assert constraint != UniqueConstraint(name="name", fields=["author"])
