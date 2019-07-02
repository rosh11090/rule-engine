# rule-engine
A simple python rule engine to parse human friendly condition.
```
fcs = [
  {
   "filter_criteria": "source(maa, del) and pax.range(2,6)",
   "flat_discount": 200, "percent_discount": 0, "max_discount": 0
  },
 {
   "filter_criteria": "sector(blr-del, del-blr) and airline(indigo, spice-jet) and pax.range(4,)",
   "flat_discount": 0, "percent_discount": 10, "max_discount": 500
 }
]
disc = Discount(fcs=fcs)
print(disc.template,  "\n")
```
 prints jinja template syntax for filtr criteria,
```
{% if (source|string in ('maa','del')) and (2 <= pax|float < 6) %}200{% endif %}
{% if (sector|string in ('blr-del','del-blr')) and (airline|string in ('indigo','spice-jet')) and (4 <= pax|float) %}{{[price*10/100, 500]|min}}{% endif %}
```

```
discount = disc.get_discount(source="maa", pax=5, sector="blr-del", airline="indigo", price=1000)
print("discount=", discount)
```
prints ```200.0```
