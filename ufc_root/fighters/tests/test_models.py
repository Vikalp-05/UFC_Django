import pytest
from django.db.utils import IntegrityError
from fighters.models import WeightClass, Fighter


@pytest.mark.django_db
def test_weightclass_str():
    wc = WeightClass.objects.create(
        name="Lightweight",
        slug="lightweight"
    )
    assert str(wc) == "Lightweight"


@pytest.mark.django_db
def test_weightclass_slug_unique():
    WeightClass.objects.create(name="A", slug="a")

    with pytest.raises(IntegrityError):
        WeightClass.objects.create(name="B", slug="a")


@pytest.mark.django_db
def test_fighter_creation():
    wc = WeightClass.objects.create(
        name="Welterweight",
        slug="welterweight"
    )

    fighter = Fighter.objects.create(
        weight_class=wc,
        rank="1",
        rank_number=1,
        name="Test Fighter",
        slug="test-fighter"
    )

    assert fighter.name == "Test Fighter"
    assert str(fighter) == "Test Fighter"


@pytest.mark.django_db
def test_fighter_slug_unique():
    wc = WeightClass.objects.create(name="A", slug="a")

    Fighter.objects.create(
        weight_class=wc,
        rank="1",
        rank_number=1,
        name="F1",
        slug="dup"
    )

    with pytest.raises(IntegrityError):
        Fighter.objects.create(
            weight_class=wc,
            rank="2",
            rank_number=2,
            name="F2",
            slug="dup"
        )