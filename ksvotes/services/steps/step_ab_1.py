# -*- coding: utf-8 -*-
from ksvotes.services.steps import Step


class Step_AB_1(Step):
    form_requirements = ["elections"]
    step_requirements = []
    endpoint = "/ab/election-picker/"
    prev_step = "Step_0"
    next_step = None

    def run(self):
        if self.is_complete:
            return True

        if not self.verify_form_requirements():
            return False

        self.is_complete = True
        if self.registrant.vr_completed_at:
            self.next_step = "Step_AB_5"  # already have address
        else:
            self.next_step = "Step_AB_3"

        return True
