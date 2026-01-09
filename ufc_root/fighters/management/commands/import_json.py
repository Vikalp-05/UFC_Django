import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from fighters.models import WeightClass, Fighter


class Command(BaseCommand):
    help = "Import UFC rankings and fighter data from JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="data/scrape_ufc.json",
            help="Path to UFC rankings JSON file",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file"])

        if not file_path.exists():
            self.stderr.write(f"File not found: {file_path}")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.stdout.write("Starting UFC JSON import...")

        for weight_class_name, fighters in data.items():
            weight_class, _ = WeightClass.objects.get_or_create(
                name=weight_class_name,
                defaults={"slug": slugify(weight_class_name)},
            )

            self.stdout.write(f"Processing {weight_class.name}")

            for fighter_data in fighters:
                name = fighter_data.get("name")
                if not name:
                    continue

                rank = fighter_data.get("rank")

                rank_number = None
                if rank != "C" and rank is not None:
                    rank_number = int(rank)


                fighter, created = Fighter.objects.update_or_create(
                    slug=slugify(name),
                    defaults={
                        "weight_class": weight_class,
                        "rank": fighter_data.get("rank"),
                        "rank_number": rank_number,
                        "name": name,
                        "ufc_url": fighter_data.get("url"),
                        "record": fighter_data.get("Record"),
                        "age": fighter_data.get("Age"),
                        "height": fighter_data.get("Height"),
                        "weight": fighter_data.get("Weight"),
                        "reach": fighter_data.get("Reach"),
                        "leg_reach": fighter_data.get("Leg Reach"),
                        "fighting_style": fighter_data.get("Fighting Style"),
                        "hometown": fighter_data.get("Hometown"),
                        "octagon_debut": fighter_data.get("Octagon Debut"),
                        "striking_accuracy": fighter_data.get("Striking Accuracy"),
                        "takedown_accuracy": fighter_data.get("Takedown Accuracy"),
                        "significant_strike_defense": fighter_data.get("Significant Strike Defense"),
                        "takedown_defense": fighter_data.get("Takedown Defense"),
                        "sig_strikes_landed": fighter_data.get("Significant Strikes Landed"),
                        "sig_strikes_absorbed": fighter_data.get("Significant Strikes Absorbed"),
                        "takedown_average": fighter_data.get("Takedown Average"),
                        "submission_average": fighter_data.get("Submission Average"),
                        "last_3_fights": fighter_data.get("Last 3 Fights"),
                        "fight_1": fighter_data.get("Fight 1"),
                        "date_1":  fighter_data.get("Date 1"),
                        "end_round_1": fighter_data.get("End Round 1"),
                        "time_1": fighter_data.get("Time 1"),
                        "method_1": fighter_data.get("Method 1"),
                        "fight_2": fighter_data.get("Fight 2"),
                        "date_2":  fighter_data.get("Date 2"),
                        "end_round_2": fighter_data.get("End Round 2"),
                        "time_2": fighter_data.get("Time 2"),
                        "method_2": fighter_data.get("Method 2"),
                        "fight_3": fighter_data.get("Fight 3"),
                        "date_3":  fighter_data.get("Date 3"),
                        "end_round_3": fighter_data.get("End Round 3"),
                        "time_3": fighter_data.get("Time 3"),
                        "method_3": fighter_data.get("Method 3"),
                    },
                )

                action = "Created" if created else "Updated"
                self.stdout.write(f"  {action}: {fighter.name}")

        self.stdout.write(self.style.SUCCESS("UFC JSON import completed successfully."))
