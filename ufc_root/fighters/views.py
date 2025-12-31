from django.shortcuts import render, get_object_or_404
from .models import WeightClass, Fighter


def weightclass_list(request):
    classes = WeightClass.objects.all().order_by("name")
    return render(
        request,
        "fighters/weightclass_list.html",
        {"classes": classes},
    )


def weightclass_detail(request, slug):
    weight_class = get_object_or_404(WeightClass, slug=slug)
    fighters = weight_class.fighters.all().order_by("rank")

    return render(
        request,
        "fighters/weightclass_detail.html",
        {
            "weight_class": weight_class,
            "fighters": fighters,
        },
    )


def fighter_detail(request, slug):
    fighter = get_object_or_404(Fighter, slug=slug)

    return render(
        request,
        "fighters/fighter_detail.html",
        {"fighter": fighter},
    )