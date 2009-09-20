"""
Defaults for nailbiter app
"""

# define image processors
PROCESSORS = (
    'nailbiter.processors.colorspace',
    'nailbiter.processors.autocrop',
    'nailbiter.processors.scale_and_crop',
    'nailbiter.processors.filters',
)
