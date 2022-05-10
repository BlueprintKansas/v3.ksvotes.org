# -*- coding: utf-8 -*-
import usaddress


def zip_code_matches(sosrec, zipcode):
    address = sosrec["Address"].replace("<br/>", " ")
    addr_parts = usaddress.tag(address)
    for key, val in addr_parts[0].items():
        if key == "ZipCode":
            if str(val).startswith(str(zipcode)):
                return True
    return False
