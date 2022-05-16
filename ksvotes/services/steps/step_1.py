# -*- coding: utf-8 -*-
from ksvotes.services.steps import Step


# this is a placeholder. No action required, just routing to change-or-apply
class Step_1(Step):
    form_requirements = []
    step_requirements = []
    endpoint = "/change-or-apply"
    prev_step = "Step_0"
    next_step = None
    is_complete = False

    def run(self):
        return True
