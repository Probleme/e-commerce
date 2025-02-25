def custom_pipeline(backend, user, response, *args, **kwargs):
    """
    Custom pipeline to handle GitHub-specific data
    """
    if backend.name == 'github':
        if not user.username and response.get('login'):
            user.username = response['login']
        
        if not user.image and response.get('avatar_url'):
            user.image = response['avatar_url']
            
        user.save()
    
    return {'user': user}