# coding=utf-8
# --=mpj17=-- I am putting this here for safe keeping.
def rename_page(self, newId):
    current_id = self.id
    parentFolder = self.context.aq_parent
    if hasattr(parentFolder.aq_explicit, new_id):
        self.status = u'<a href="%s">A page with identifier '\
        '<code class="page">%s</code></a> already exists '\
        u'in this folder' % (new_id, new_id)
        retval = None
    else:
        folder.manage_renameObject(current_id, new_id)
        retval = getattr(folder.aq_explicit, new_id, None)
        newURL = retval.absolute_url(0)
        self.status = 'Page renamed'
    return retval


