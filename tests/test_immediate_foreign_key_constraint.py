import pytest
from django.db import IntegrityError
from django_subatomic import db

from .books.models import Book


@pytest.mark.django_db(transaction=True)
def test_immediate_foreign_key_integrity_error():
    with db.transaction():
        with pytest.raises(IntegrityError):
            Book.objects.create(author_id=-1)
