def asset_upload_path(instance, filename):
    """Generate a dynamic upload path for website assets based on the instance and filename."""
    model = instance.__class__.__name__

    if model == "Page":
        return f"{instance.website.name}/staging/pages/{filename}"
    elif model == "Website":
        if filename.endswith((".css", ".js")):
            return f"{instance.name}/staging/static/{filename}"

        return f"{instance.name}/staging/{filename}"

    elif model == "Asset":
        if instance.type == "image":
            return f"{instance.website.name}/staging/asset/images/{filename}"
        elif instance.type == "video":
            return f"{instance.website.name}/staging/asset/videos/{filename}"
