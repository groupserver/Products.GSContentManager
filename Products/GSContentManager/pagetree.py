# coding=utf-8
from zope.interface import implements, providedBy, implementedBy,\
  directlyProvidedBy, alsoProvides, Interface
from zope.component import adapts, createObject, provideAdapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.contentprovider.interfaces import IContentProvider
from Products.XWFCore.XWFUtils import munge_date
from interfaces import *
from page import Page

class GSPageTreeContentProvider(object):
    
    implements( IGSPageTreeContentProvider )
    adapts(Interface, IDefaultBrowserLayer, Interface)

    def __init__(self, context, request, view):
        
        self.__parent__ = self.view = view
        self.__updated = False

        self.context = context
        self.request = request
        self.pageTree = None
        
    def update(self):
        self.__updated = True
        tree = PageTree(self.context)
        self.pageTree = tree.tree
        
    def render(self):
        if not self.__updated:
            raise interfaces.UpdateNotCalled
        # --=mpj17=-- Unusually, this content provider does not use
        #   a page template, because TAL does not support recursion.
        #   Instead all the creation is done by ulTree.
        return self.ulTree
                
    #########################################
    # Non standard methods below this point #
    #########################################

    @property
    def ulTree(self):
        '''The tree as an unordered list'''
        retval = u'<ul class="pageTree">\n%s\n</ul>' % \
          self.node_to_li(self.pageTree)
        return retval

    def node_to_li(self, node):
        '''Convert a node into an HTML li
        
        ARGUMENTS
          node  The node to convert.
        
        RETURNS
          A Unicode string that contains the li.
          
        SIDE EFFECTS
          None.
        '''
        
        page = Page(node[0])
        t = '%(name)s, last edited by %(fn)s on %(date)s' % \
          {'name': page.name,
           'date': munge_date(self.context, page.date), 
           'fn':   page.editor.name}
        retval = u'<li id="%(nodeId)s">\n\t<a title="%(title)s" '\
          u'href="%(url)s"><cite>%(name)s</cite> '\
          u'<code>(%(id)s)</code></a>' % {
            'title': t,
            'url': page.url,
            'name': page.name,
            'id': page.id,
            'nodeId': url_to_nodeId(self.treeIdPrefix, page.url)
        }
        if node[1]:
            cLi = u'\n'.join(self.node_to_li(c) for c in node[1])
            retval = u'%s\n<ul>\n%s\n</ul>\n</li>' % (retval, cLi)
        else:
            retval = u'%s\n</li>' % retval
        assert retval
        assert type(retval) == unicode
        return retval
        
class PageTree(object):
    '''A representation of a tree of pages as a list of lists.
    
    The methods here are old-skool COSC121 depth-first tree walking
    algorithms. The class itself is just a big ol' wrapper for the
    "tree" property. I remember this being a lot more difficult.
    
    PROPERTIES
      tree    The tree as a 2-tuple: (node, children).
    
    '''
    def __init__(self, folder):
        '''Create a tree.
        
        ARGUMENTS
          folder  A folder, any folder, in the tree.
        '''
        assert IGSContentManagerFolderMarker in providedBy(folder)
        self.context = self.folder = folder
        self.__tree = None

    @property
    def tree(self):        
        '''Get the tree as a 2-tuple: (node, children). Each child is
           represented as a 2-tuple of (node, children).
        '''
        if self.__tree == None:
            self.__tree = self.get_tree(self.get_root(self.folder))
        retval = self.__tree
        assert retval
        assert len(retval) == 2
        assert IGSContentManagerFolderMarker in providedBy(retval[0])
        return retval

    def get_root(self, node):
        '''Get the root of the page-tree

        The root node is a node that provides the 
        IGSContentManagerFolderMarker interface but does not have a
        parent that provides the IGSContentManagerFolderMarker 
        interface.
        
        ARGUMENTS
          node  A node in the tree to start searching from.
          
        RETURNS
          The root node of the tree.
          
        SIDE EFFECTS
          None
        '''
        parent = node.aq_parent
        if (IGSContentManagerFolderMarker in providedBy(parent)):
            retval = self.get_root(parent)
        else:
            retval = node
        assert retval
        assert IGSContentManagerFolderMarker in providedBy(retval)
        return retval
        
    def get_tree(self, node):
        '''Get the tree below of the node
        
        ARGUMENTS
            A node in the tree.
            
        RETURNS
            A 2-tuple of (node, (children\ldots)). The node supports
            the IGSContentManagerFolderMarker interface.
            
        SIDE EFFECTS
            None
        '''
        assert IGSContentManagerFolderMarker in providedBy(node)
        
        objectValueTypes = ('Folder (Ordered)', 'Folder')
        childFolders = node.objectValues(objectValueTypes)
        children = [self.get_tree(c) for c in childFolders 
                    if(IGSContentManagerFolderMarker in providedBy(c))]
        retval = (node, tuple(children))
        
        assert len(retval) == 2
        assert retval[0] == node
        assert IGSContentManagerFolderMarker in providedBy(retval[0])
        return retval

        
def url_to_nodeId(treeIdPrefix, url):
    retval = url.lstrip('http\:\/\/')
    retval = retval.replace('-', '--')
    retval = retval.replace('/', '-')
    retval = '%s%s' % (treeIdPrefix, retval)
    return retval
        
provideAdapter(GSPageTreeContentProvider,
    provides=IContentProvider,
    name="groupserver.PageTree")

