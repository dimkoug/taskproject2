(function($){
  $('.order').on('click', function(e){
      e.preventDefault();
      var url_link = $(this).data('url');
      $.ajax({
          url: url_link,
          method: 'GET',
          data: {order_by: $(this).data('order')},
          datatype: 'json',
          success: function(result){
            $("#result").html(result.result);
          }
      });
  })
})(jQuery)
