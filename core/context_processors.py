def base_template(request):
    user = getattr(request, 'user', None)
    role = None
    if user and user.is_authenticated:
        role = getattr(user, 'role', None)

    if role:
        role_key = role.lower().strip()
        if role_key == 'customer':
            return {'base_template': 'estate/base.html'}
        if role_key in ['agent', 'company']:
            return {'base_template': f'{role_key}/base.html'}
    return {'base_template': 'estate/base.html'}
