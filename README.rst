=============================================================
``django-nailbiter`` - a storage-agnostic thumbnail generator
=============================================================

``nailbiter`` is a simple thumbnail generation field for Django,
modeled after ``sorl-thumbnail``. 


Usage
=====

First, define a model using a ``nailbiter`` thumbnail field:

In ``models.py``::

	from django.contrib.auth.models import User
	from django.db import models
	from nailbiter.fields import ImageWithThumbsField

	class Gallery(models.Model):
	    name = models.CharField(max_length=150)
		

	class Photo(models.Model):
	    uploader = models.ForeignKey(User, related_name="photos")
	    gallery = models.ForeignKey(Gallery, related_name="photos")
	    title = models.CharField(max_length=150)
	    image_file = ImageWithThumbsField(
	        upload_to = photo_upload_path,
	        generate_on_save = True,
	        thumbnail = {'size': (150, 150), 'options': ['detail']},
	        extra_thumbnails = {
	            'headline': {'size': (300, 300), 'options': ['upscale', 'detail']},
	            'avatar': {'size': (64, 64), 'options': ['crop', 'upscale', 'detail']},
	            'gallery_icon': {'size': (150, 150), 'options': ['crop', 'upscale', 'detail']}})
	    created_date = models.DateTimeField(default=datetime.utcnow)

To display the thumbnail in a template: ::

	<img src="{{ object.image_file.thumbnail.url }}" />
	
To display a thumbnail defined in ``extra_thumbnails``, just refer to it
by the name you defined: ::

	<img src="{{ object.image_file.headline.url }}" />