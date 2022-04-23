def fix_perms(request):
    if not request.user.is_authenticated:
        perms = []
    else:
        perms = request.user.account_type.get_user_permissions()
    return {"perms": perms}
