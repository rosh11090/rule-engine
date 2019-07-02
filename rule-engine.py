import jinja2
import re


class ComparableUndefined(jinja2.Undefined):
    """
        Handle exception if any of the attribute is not provided
    """
    def __ne__(self, other):
        return False
    def __eq__(self, other):
        return False
    def __lt__(self, other):
        return False
    def __gt__(self, other):
        return False
    def __le__(self, other):
        return False
    def __ge__(self, other):
        return False
    def __contains__(self, other):
        return False
    def __call__(self, *args, **kwargs):
        return False

jenv = jinja2.Environment(undefined=ComparableUndefined)

def safe_int(n):
    try: return int(n)
    except Exception: return 0

class Discount(object):
    def __init__(self, fcs = []):
        self.template = ""
        self.compile(fcs)
        self.tmpl_func = jenv.from_string(self.template)

    @staticmethod
    def get_snippet_template(fc_text, flat_discount, percent_discount, max_discount):
        """
        return template for each filter criteria
        """
        flat_discount = safe_int(flat_discount)
        percent_discount = safe_int(percent_discount)
        max_discount = safe_int(max_discount)
        value_text = flat_discount if flat_discount else f"{{{{[price*{percent_discount}/100, {max_discount}]|min}}}}"
        return f'{{% if {fc_text} %}}{value_text}{{% endif %}}'


    def fc_substitute(self, matchobj):
        a, b = matchobj.group(0).strip(')').split('(')
        b = map(str.strip, b.split(","))
        if a.endswith(".range"):
            b = list(b)
            assert len(b)==2, f"invalid argument {b} for range"
            _min, _max = b
            if _min and _max:
                return f"({_min} <= {a.rstrip('.range')}|float < {_max})"
            if _min:
                return f"({_min} <= {a.rstrip('.range')}|float)"
            if _max:
                return f"({a.rstrip('.range')}|float < {_max})"
            return "False"
        else:
            b = map(lambda x: "'" + x + "'", b)
            return f"({a}|string in ({','.join(b)}))"

    def get_template_text(self, filter_criteria, flat_discount, percent_discount, max_discount):
        """
        return a valid template for each rule
        if any filter criteria is invalid it will print exception here.
        """
        try:
            fc_text = re.sub('[a-z0-9_]+(\.range)?\([A-Za-z0-9_ ,.-]+\)', self.fc_substitute, filter_criteria)
            jinja_string = Discount.get_snippet_template(fc_text, flat_discount, percent_discount, max_discount)
            #below line will trhow exception in case of any typos or exeption
            jenv.from_string(jinja_string).render(price=34)
            return jinja_string
        except Exception as e:
            print("Error parsing filter citeria", e)
            return ''

    def compile(self, fcs):
        def helper():
            # row = {'filter_criteria': fc, flat_discount: 0, percent_discount: 0, max_discount: 0}
            for row in fcs:
                yield self.get_template_text(**row)
        self.template = "\n".join(helper())

    def get_discount(self, **kwargs):
        data = self.tmpl_func.render(**kwargs)
        return max([float(i) for i in map(str.strip, data.split("\n")) if i] or [0])


if __name__ == "__main__":
    fcs = [
        {'filter_criteria': "source(maa, del) and pax.range(2,6)", "flat_discount": 200, "percent_discount": 0, "max_discount": 0},
        {'filter_criteria': "sector(blr-del, del-blr) and airline(indigo, spice-jet) and pax.range(4,)", "flat_discount": 0, "percent_discount": 10, "max_discount": 500}

    ]
    disc = Discount(fcs=fcs)
    # cache this disc for time untill no filter criteria is added.
    print(disc.template,  "\n")
    discount = disc.get_discount(source="maa", pax=5, sector="blr-del", airline="indigo", price=1000)
    print("discount=", discount)
