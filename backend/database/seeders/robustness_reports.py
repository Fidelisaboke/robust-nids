import json
import os

from database.db import db
from database.models import RobustnessReport
from database.seeders import BaseSeeder


class RobustnessReportSeeder(BaseSeeder):
    """Seeder for robustness reports"""

    @classmethod
    def run(cls):
        # Path to adversarial_experiment.json
        report_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../../backend/ml/models/artifacts/adversarial_experiment.json",
            )
        )

        with db.get_session() as session:
            existing_reports = {(r.model, r.accuracy) for r in session.query(RobustnessReport).all()}

            # Load metrics from file
            with open(report_path, "r") as f:
                raw_data = json.load(f)

            # Compose metrics for seeding (FGSM, epsilon=0.1)
            sample_reports = [
                {
                    "model": "Baseline (on Normal Data)",
                    "accuracy": raw_data["baseline_clean_acc"],
                },
                {
                    "model": "Baseline (on FGSM Attack)",
                    "accuracy": raw_data["baseline_results"]["epsilons"]["0.1"]["fgsm"]["acc"],
                },
                {
                    "model": "Robust Model (on Normal Data)",
                    "accuracy": raw_data["robust_clean_acc"],
                },
                {
                    "model": "Robust Model (on FGSM Attack)",
                    "accuracy": raw_data["robust_results"]["epsilons"]["0.1"]["fgsm"]["acc"],
                },
            ]

            reports_to_create = []
            for report in sample_reports:
                if (report["model"], report["accuracy"]) not in existing_reports:
                    reports_to_create.append(
                        RobustnessReport(model=report["model"], accuracy=report["accuracy"])
                    )

            if reports_to_create:
                session.add_all(reports_to_create)
                session.commit()
                cls.log_seeding("RobustnessReport", len(reports_to_create))
            else:
                print("⏩ Robustness reports already seeded, skipping...")
