def fix_perms(request):
    return {"perms": request.user.account_type.get_user_permissions()}
