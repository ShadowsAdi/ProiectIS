def theme(request):
    if request.user.is_authenticated:
        return {'theme': request.user.settings.theme}
    return {'theme': 'light'}