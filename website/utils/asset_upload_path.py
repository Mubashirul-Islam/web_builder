from website.models import Page, Website, Asset


def asset_upload_path(instance, filename):
    """Generate a dynamic upload path for website assets based on the instance and filename."""
    model = instance.__class__.__name__

    if model == Page.__name__:
        return f"{instance.website.name}/staging/pages/{filename}"
    elif model == Website.__name__:
        if filename.endswith((".css", ".js")):
            return f"{instance.name}/staging/static/{filename}"

        return f"{instance.name}/staging/{filename}"

    elif model == Asset.__name__:
        if instance.type == Asset.AssetType.IMAGE:
            return f"{instance.website.name}/staging/asset/images/{filename}"
        elif instance.type == Asset.AssetType.VIDEO:
            return f"{instance.website.name}/staging/asset/videos/{filename}"
