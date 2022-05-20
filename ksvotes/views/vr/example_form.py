# -*- coding: utf-8 -*-
signature_img_string = "data:image/png;base64,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"
