def asset_upload_path(instance, filename):
    '''Determines the upload path for asset files based on the instance's model and attributes.'''
    model = instance._meta.model_name
    if model == "Website" and instance.name:
        return f"{instance.name}/{filename}"

    if model == "Page" and instance.website and instance.website.name:
        return f"{instance.website.name}/{filename}"

    return filename