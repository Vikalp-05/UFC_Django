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

from django.shortcuts import render
from .models import WeightClass, Fighter

def weightclass_list(request):
    cards = []
    for wc in WeightClass.objects.all().order_by("name"):
        fighters = list(Fighter.objects.filter(weight_class=wc))

        def sort_key(f):
            r = str(f.rank).strip().upper()
            if r == "C":
                return (0, 0)          # champion first
            return (1, int(r))         # then 1,2,3...

        fighters = sorted(fighters, key=sort_key)[:6]  # champ + 1–5
        cards.append({"wc": wc, "top": fighters})

    return render(request, "fighters/weightclass_list.html", {"cards": cards})
