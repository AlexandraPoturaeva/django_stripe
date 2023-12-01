 function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


/*
The code below is an event handler to the "click" event
on the element (button) with class contained "add-item-to-order".
Function gets item_id and passes it through ajax post request to url "/add-item-to-order/".
If success, it gets data back and put it into the text of "buy_items_button".
*/
 $(document).on("click", ".add-item-to-order", function () {
         var item_id = $(this).data('item-id');
         let buy_items_button = $('.buy_items_button');
         $.ajax({
            url: "/add-item-to-order/",
            headers: {'X-CSRFToken': csrftoken},
            data: {
                "item_id": item_id,
                },
            type: 'post',
            success: function(data)
            {
                buy_items_button.prop('disabled', false);
                buy_items_button.html(
                'Buy ' + data.items_in_order_cnt + ' items for $' + data.order_total_cost
                );
            },
            error: function(error)
            {
                $('.space-for-messages').text('Что-то пошло не так...').css("color", "red");
            },
        });
        setTimeout(function() {
                    $('.space-for-messages').empty();
                    }, 4000);
});
