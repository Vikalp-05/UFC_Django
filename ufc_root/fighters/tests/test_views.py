import pytest
from django.urls import reverse
from fighters.models import WeightClass, Fighter


@pytest.fixture
def weightclass():
    return WeightClass.objects.create(
        name="Middleweight",
        slug="middleweight"
    )


@pytest.fixture
def fighters(weightclass):
    champ = Fighter.objects.create(
        weight_class=weightclass,
        rank="C",
        rank_number=0,
        name="Champion",
        slug="champion"
    )

    contender = Fighter.objects.create(
        weight_class=weightclass,
        rank="1",
        rank_number=1,
        name="Contender",
        slug="contender"
    )

    return champ, contender


@pytest.mark.django_db
def test_weightclass_list_view(client):
    response = client.get(reverse("weightclass_list"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_weightclass_detail_view(client, weightclass, fighters):
    response = client.get(
        reverse("weightclass_detail", args=[weightclass.slug])
    )
    assert response.status_code == 200
    assert "Champion" in response.content.decode()


@pytest.mark.django_db
def test_weightclass_detail_404(client):
    response = client.get(
        reverse("weightclass_detail", args=["invalid"])
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_fighter_detail_view(client, fighters):
    champ, _ = fighters
    response = client.get(
        reverse("fighter_detail", args=[champ.slug])
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_fighter_detail_404(client):
    response = client.get(
        reverse("fighter_detail", args=["invalid"])
    )
    assert response.status_code == 404