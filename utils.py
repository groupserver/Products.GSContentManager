# coding=utf-8
from datetime import datetime
import pytz
from interfaces import IGSContentPageVersion

CONTENT_TEMPLATE = 'content_en'

def new_version(folder, newId):
    '''Create a new (blank) version of a document'''
    manageAdd = folder.manage_addProduct['PageTemplates']
    # --=mpj17=-- If the text is not set, the page template will
    #   try and acquire the text from its parent when the form
    #   tries to set the text. (I know, do not get me started.)
    #   By setting the text here we stop the madness.
    manageAdd.manage_addPageTemplate(newId, title='', 
      text='GSNotSet', REQUEST=None)
    template = getattr(folder, newId)
    assert template.getId() == newId
    assert template.meta_type == 'Page Template'
    retval = IGSContentPageVersion(template)
    assert retval
    return retval

def new_version_id():
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    t = now.strftime("%Y%m%d%H%M%S")
    retval = '%s_%s' % (CONTENT_TEMPLATE, t)
    assert type(retval) == str
    assert retval
    return retval

