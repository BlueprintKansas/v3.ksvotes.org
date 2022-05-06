# -*- coding: utf-8 -*-
from django.shortcuts import render

def stats(request): # TODO
    ninety_days = datetime.timedelta(days=90)
    today = datetime.date.today()
    s = RegistrantStats()
    vr_stats = s.vr_through_today(today - ninety_days)
    ab_stats = s.ab_through_today(today - ninety_days)

    stats = {'vr': [], 'ab': []}
    for r in vr_stats:
      stats['vr'].append(r.values())
    for r in ab_stats:
      stats['ab'].append(r.values())

    return render(request, 'stats.html', { "stats": stats })

def terms(request):
    return render(request, 'terms.html')


def privacy(request):
    return render(request, 'privacy-policy.html')


def about(request):
    return render(request, 'about.html')

