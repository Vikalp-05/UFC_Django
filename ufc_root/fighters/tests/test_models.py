import pytest
from fighters.models import WeightClass, Fighter


@pytest.mark.django_db
def test_weightclass_creation():
    wc = WeightClass.objects.create(name="Lightweight", slug="lightweight")
    assert wc.name == "Lightweight"
    assert str(wc) == "Lightweight"


@pytest.mark.django_db
def test_fighter_creation():
    wc = WeightClass.objects.create(name="LW", slug="lw")

    fighter = Fighter.objects.create(
        name="Test Fighter",
        slug="test-fighter",
        weight_class=wc,
        rank="1",
        record="10-0-0"
    )

    assert fighter.name == "Test Fighter"
    assert fighter.weight_class == wc
    assert fighter.record == "10-0-0"