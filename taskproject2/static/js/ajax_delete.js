(function($){
    $(document).ready(function(){
      $('.delete').on('click', function(e){
          e.preventDefault();
          var that = $(this);
          var url = $(this).attr('href');
          var c = confirm("Delete the object");
          if (c == true) {
            $.post(url, function( data ) {
              $(that).parent().parent().fadeOut();
            });
          }
          return false;
      })
    });
})(jQuery)
