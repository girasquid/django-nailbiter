from cStringIO import StringIO
from os.path import splitext as split_ext, split as split_path, join as join_path
from PIL import Image

from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from django.core.files.base import ContentFile

def generate_thumbnail(img, size, options):
    """
    Generates a thumbnail image and returns a ContentFile object with the thumbnail
    
    `img`: `PIL.Image` object
    `thumb`: thumbnail dimensions as tuple
    `format`: source image's format (eg, `jpeg`, `gif`, `png`). 
              thumbnails will preserve this type.
    """
    # from nailbiter import processors
    from nailbiter import defaults as default_procs
    from nailbiter.processors import dynamic_import
    
    img.seek(0) # seek to beginning of image data
    image = Image.open(img)
    
    # convert to rgb if necessary
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')

    for proc in options:
        # apply options and filters from `field.options`
        # processor = getattr(processors, proc)
        processors = dynamic_import(default_procs.PROCESSORS)
        for processor in processors:
            image = processor(image, size, options)
    
    io = StringIO()
    
    if image.format is None:
        format = 'JPEG'
    elif image.format.upper()=='JPG':
        format = 'JPEG'
    else:
        format = image.format
    
    image.save(io, format)
    return ContentFile(io.getvalue())    


class NailbiterThumbnail(object):    
    def __init__(self, name, height, width, url):
        self.name = name
        self.height = height
        self.width = width
        self.url = url


class ImageWithThumbsFieldFile(ImageFieldFile):
    """``ImageFieldFile`` implementation offering compatibility with
    custom storage backends, and allowing multiple thumbnail definitions.
    
    On load, store a list of all thumbnails, and add properties
    for each thumbnail to return a ``NailbiterThumbnail`` object.
    
    """
    
    def __init__(self, *args, **kwargs):
        super(ImageWithThumbsFieldFile, self).__init__(*args, **kwargs)
        self.thumbnails_to_generate = []
        
        # queue `thumbnail` option
        if self.field.thumbnail:
            self.thumbnails_to_generate.append({
                'name': "thumbnail", 
                'options': self.field.thumbnail.get('options', []),
                'size': self.field.thumbnail['size']})
            
            if self:
                setattr(self, "thumbnail", NailbiterThumbnail(
                    "thumbnail",
                    self.field.thumbnail['size'][1],
                    self.field.thumbnail['size'][0],
                    self._generate_thumbnail_url("thumbnail", self.field.thumbnail['size'])))
        
        # queue `extra_thumbnails` 
        if self.field.extra_thumbnails:
            setattr(self, "extra_thumbnails", {})
            
            for name, details in self.field.extra_thumbnails.iteritems():                
                self.thumbnails_to_generate.append({
                    'name': name,
                    'options': details.get('options', []),
                    'size': details['size']})
                if self:
                    self.extra_thumbnails[name] = NailbiterThumbnail(
                        name,
                        details['size'][1],
                        details['size'][0],
                        self._generate_thumbnail_url(name, details['size']))
    
    def generate_thumbnail_name(self, raw_name, thumb_name, size):
        """
        Return a thumbnail file path like::
        
            `path/to/thumb_name-raw_name-sizes[0]xsizes[1].jpg`
        
        """
        filepath, filename = split_path(raw_name)
        fn, ext = split_ext(filename)
        thumbnail_filename = "%s-%s-%sx%s%s" % (
            thumb_name, fn, size[0], size[1], ext)
            
        # join path and new filename
        thumbnail_full_path = join_path(filepath, thumbnail_filename)
        
        return thumbnail_full_path
        
    def _generate_thumbnail_url(self, thumb_name, size):
        from urlparse import urlparse
        
        _url = self.url
        _name = self.name
        urlbits = urlparse(self.url)
        filename = self.generate_thumbnail_name(self.name, thumb_name, size)
        thumbnail_url = "%s://%s/%s" % (urlbits[0], urlbits[1], filename)
        
        return thumbnail_url
    
    def save(self, name, content, save=True):
        """
        Save the field's data, and generate thumbnails 
        from `self.thumbnails_to_generate`
        """
        
        # save field data
        super(ImageWithThumbsFieldFile, self).save(name, content, save)
    
        # generate thumbnails
        for thumbnail in self.thumbnails_to_generate:
            filename = self.generate_thumbnail_name(self.name, thumbnail['name'], thumbnail['size'])
        
            # generate the thumbnail
            thumbnail_data = generate_thumbnail(
                content, 
                thumbnail['size'], 
                thumbnail['options'])
            
            # store thumbnail data
            stored_filename = self.storage.save(filename, thumbnail_data)
            
    def delete(self, save=True):
        name = self.name
        super(ImageWithThumbsFieldFile, self).delete(save)
        
        for thumbnail in self.thumbnails_to_generate:
            filename = self.generate_thumbnail_name(name, thumbnail['name'], thumbnail['size'])
            
            try:
                self.storage.delete(filename)
            except:
                pass
                

class ImageWithThumbsField(ImageField):
    attr_class = ImageWithThumbsFieldFile

    def __init__(self, verbose_name=None, name=None, 
        width_field=None, height_field=None, 
        generate_on_save=True, thumbnail={}, extra_thumbnails=[], filters=[], 
        **kwargs):
        
        self.verbose_name=verbose_name
        self.name=name
        self.width_field=width_field
        self.height_field=height_field
        # self.sizes = sizes
        
        # sorl-like options
        self.generate_on_save = generate_on_save
        self.thumbnail = thumbnail
        self.extra_thumbnails = extra_thumbnails
        self.filters = filters
        
        super(ImageField, self).__init__(**kwargs)