(function($){
    $(document).ready(function(){
      $('.page').on('click', function(e){
          e.preventDefault();
          $(".pagination li").removeClass("active");
          var url_link = $(this).attr('href');
          $(this).parent().toggleClass('active');
          $.ajax({
              url: url_link,
              method: 'GET',
              datatype: 'json',
              success: function(result){
                $("#result").html(result.result);
              }
          });
      })
    });
})(jQuery)
