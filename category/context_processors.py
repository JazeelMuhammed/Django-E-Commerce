from .models import League, Club


def dropdown_menu(request):
    leagues = League.objects.all().order_by('id')
    clubs = Club.objects.all()
    return dict(leagues=leagues, clubs=clubs)

