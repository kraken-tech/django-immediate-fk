test-sqlite:
    pytest

test-postgres:
    DATABASE_URL="postgres:///immediate-fk" pytest

coverage:
    coverage erase
    coverage run -m pytest
    DATABASE_URL="postgres:///immediate-fk" coverage run -m pytest
    coverage report
