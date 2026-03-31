from pathlib import Path

from website.constants import ModelNames, AssetTypes


def upload_path(instance, filename: str) -> str:
    """Generate a dynamic upload path for website assets based on the instance and filename."""

    model = instance.__class__.__name__

    if model == ModelNames.PAGE:
        return str(Path(instance.website.name) / "staging" / "pages" / filename)
    elif model == ModelNames.WEBSITE:
        if filename.endswith((".css", ".js")):
            return str(Path(instance.name) / "staging" / "static" / filename)

        return str(Path(instance.name) / "staging" / filename)

    elif model == ModelNames.ASSET:
        if instance.type == AssetTypes.IMAGE:
            return str(
                Path(instance.website.name) / "staging" / "asset" / "images" / filename
            )
        elif instance.type == AssetTypes.VIDEO:
            return str(
                Path(instance.website.name) / "staging" / "asset" / "videos" / filename
            )

    raise ValueError(f"Unsupported upload path context for model '{model}'.")
