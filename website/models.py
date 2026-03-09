from django.db import models
from django.core.validators import FileExtensionValidator

from django.contrib.auth.models import User

def asset_upload_path(instance, filename):
	if hasattr(instance, "name") and instance.name:
		return f"{instance.name}/{filename}"

	if hasattr(instance, "website") and instance.website and instance.website.name:
		return f"{instance.website.name}/{filename}"

	return filename

class Website(models.Model):
	'''Model representing a website.'''
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="websites")
	name = models.CharField(max_length=255, unique=True)
	description = models.TextField(blank=True, default="")
	url = models.URLField(max_length=500, unique=True)
	css =  models.FileField(upload_to=asset_upload_path,
						   validators=[FileExtensionValidator(allowed_extensions=["css"])],)
	js =  models.FileField(upload_to=asset_upload_path,
						   validators=[FileExtensionValidator(allowed_extensions=["js"])],)
	header = models.FileField(upload_to=asset_upload_path,
						   validators=[FileExtensionValidator(allowed_extensions=["html"])],)
	footer = models.FileField(upload_to=asset_upload_path,
						   validators=[FileExtensionValidator(allowed_extensions=["html"])],)
	created_at = models.DateTimeField(auto_now_add=True)
	modified_at = models.DateTimeField(auto_now=True, db_index=True)

	def __str__(self):
		return self.name


class Page(models.Model):
	'''Model representing a page within a website.'''
	website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="pages")
	title = models.CharField(max_length=255, db_index=True)
	slug = models.SlugField(max_length=255)
	content = models.FileField(upload_to=asset_upload_path,
						   validators=[FileExtensionValidator(allowed_extensions=["html"])],)
	created_at = models.DateTimeField(auto_now_add=True)
	modified_at = models.DateTimeField(auto_now=True, db_index=True)

	def __str__(self):
		return self.title
