import pytest
from django.urls import reverse
from fighters.models import WeightClass, Fighter


@pytest.mark.django_db
def test_champion_first(client):
    wc = WeightClass.objects.create(
        name="Featherweight",
        slug="featherweight"
    )

    Fighter.objects.create(
        weight_class=wc,
        rank="2",
        rank_number=2,
        name="Rank2",
        slug="r2"
    )

    Fighter.objects.create(
        weight_class=wc,
        rank="C",
        rank_number=0,
        name="Champion",
        slug="champ"
    )

    Fighter.objects.create(
        weight_class=wc,
        rank="1",
        rank_number=1,
        name="Rank1",
        slug="r1"
    )

    response = client.get(
        reverse("weightclass_detail", args=[wc.slug])
    )

    fighters = list(response.context["fighters"])

    assert fighters[0].rank == "C"
    assert fighters[1].rank_number == 1
    assert fighters[2].rank_number == 2