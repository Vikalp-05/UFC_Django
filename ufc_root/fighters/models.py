from django.db import models

class WeightClass(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class Fighter(models.Model):
    weight_class = models.ForeignKey(
        WeightClass,
        on_delete=models.CASCADE,
        related_name="fighters"
    )

    #Misc.
    rank = models.CharField(max_length=5)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    ufc_url = models.URLField(blank=True, null=True)

    #Bio
    age = models.CharField(max_length=10, blank=True, null=True)
    height = models.CharField(max_length=20, blank=True, null=True)
    weight = models.CharField(max_length=20, blank=True, null=True)
    reach = models.CharField(max_length=20, blank=True, null=True)
    leg_reach = models.CharField(max_length=20, blank=True, null=True)
    octagon_debut = models.CharField(max_length=50, blank=True, null=True)
    fighting_style = models.CharField(max_length=50, default="MMA")
    hometown = models.CharField(max_length=120, blank=True, null=True)
    record = models.CharField(max_length=20, blank=True, null=True)

    #Statistics
    striking_accuracy = models.CharField(max_length=10, blank=True, null=True)
    takedown_accuracy = models.CharField(max_length=10, blank=True, null=True)
    significant_strike_defense = models.CharField(max_length=10, blank=True, null=True)
    takedown_defense = models.CharField(max_length=10, blank=True, null=True)
    sig_strikes_landed = models.CharField(max_length=10, blank=True, null=True)
    sig_strikes_absorbed = models.CharField(max_length=10, blank=True, null=True)
    takedown_average = models.CharField(max_length=10, blank=True, null=True)
    submission_average = models.CharField(max_length=10, blank=True, null=True)
    last_3_fights = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name

