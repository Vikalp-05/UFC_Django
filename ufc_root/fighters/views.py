from django.shortcuts import render, get_object_or_404
from django.db.models import Case, When, IntegerField
from django.http import HttpResponseRedirect
from django.core.mail import send_mail, get_connection
from .contact import ContactForm
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
    fighters = (
        Fighter.objects
        .filter(weight_class=weight_class)
        .annotate(
            sort_rank=Case(
                When(rank="C", then=0),          # Champion first
                default=1,
                output_field=IntegerField(),
            )
        )
        .order_by("rank_number")
    )

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

def contact(request):
	submitted = False
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			con = get_connection('django.core.mail.backends.console.EmailBackend')
			send_mail(
				cd['subject'],
				cd['message'],
				cd.get('email', 'noreply@dcu.ie'),
				['student@dcu.ie'], # change this
				connection=con
			)
			return HttpResponseRedirect('/contact?submitted=True')
	else:
		form = ContactForm()
		if 'submitted' in request.GET:
			submitted = True
	context = {
		'form': form,
		'page_list': Fighter.objects.all(),
		'submitted': submitted
	}
	return render(request, 'registration/contact.html', context)