
var options = {
  skinPath: '/++resource++gswymskin/gs/',
  skin: 'gs',
  langPath: '/++resource++wymeditor-20090831/wymeditorlang/',
  dialogFeatures: "menubar=no,titlebar=no,toolbar=no,resizable=no,width=504,height=504,top=0,left=0",
};
jQuery(document).ready( function() {
    jQuery('#form\\.actions\\.change').addClass('wymupdate');
    jQuery('.wymeditor').wymeditor(options);
});

