$(function (){
    const stripe_pk = JSON.parse(document.getElementById('stripe_pk').textContent);
    const backend_domain = JSON.parse(document.getElementById('backend_domain').textContent);
    const stripe = Stripe(stripe_pk);

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
        let item_id = $(this).data('item-id');
        let order_info = $('.order-info');
        let pay_order_with_checkout_button = $('.pay-order-with-checkout');
        let show_payment_intent_form_button = $('.show-payment-intent-form');
        $.ajax({
            url: "/add-item-to-order/",
            headers: {'X-CSRFToken': csrftoken},
            data: {
                "item_id": item_id,
                },
            type: 'post',
            success: function(data)
            {
                pay_order_with_checkout_button.prop('disabled', false);
                show_payment_intent_form_button.prop('disabled', false);
                show_payment_intent_form_button.data('order-id', data.order_id);
                order_info.text(
                'Buy ' + data.items_in_order_cnt + ' items for $' + data.order_total_cost
                );
            },
            error: function(error)
            {
                $('.space-for-messages').text('Something went wrong.').css("color", "red");
            },
        });
        setTimeout(function() {
            $('.space-for-messages').empty();
            }, 4000);
    });

    // ------- setting stripe payment intent -------
    let elements;

    $(document).on("click", ".show-payment-intent-form", function (){
        initialize(
            $(this).data('fetch-url'),
            $(this).data('order-id')
        );
    });

    checkStatus();

    const el = document.querySelector("#payment-form");
    if (el) {
      el.addEventListener("submit", handleSubmit);
    }

    // Fetches a payment intent and captures the client secret
    async function initialize(fetch_url, order_id) {
        const response = await fetch(fetch_url + order_id + "/", {
            method: "POST",
            headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
            },
        });

        const { clientSecret } = await response.json();

        const appearance = {
            theme: 'stripe',
        };
        elements = stripe.elements({ appearance, clientSecret });

        const paymentElementOptions = {
            layout: "tabs",
        };

        const paymentElement = elements.create("payment", paymentElementOptions);
        paymentElement.mount("#payment-element");
    }

    async function handleSubmit(e) {
        e.preventDefault();
        setLoading(true);
        let order_id = $('.show-payment-intent-form').data('order-id')
        const { error } = await stripe.confirmPayment({
            elements,
            confirmParams: {
                return_url: backend_domain + "/payment-intent-result/?order_id=" + order_id,
            },
        });

        // This point will only be reached if there is an immediate error when
        // confirming the payment. Otherwise, your customer will be redirected to
        // your `return_url`. For some payment methods like iDEAL, your customer will
        // be redirected to an intermediate site first to authorize the payment, then
        // redirected to the `return_url`.
        if (error.type === "card_error" || error.type === "validation_error") {
            showMessage(error.message);
        } else {
            showMessage("An unexpected error occurred.");
        }

        setLoading(false);
    }

    // Fetches the payment intent status after payment submission
    async function checkStatus() {
        const clientSecret = new URLSearchParams(window.location.search).get(
            "payment_intent_client_secret"
        );
        let order_id = new URLSearchParams(window.location.search).get(
            "order_id"
        );

        if (!clientSecret) {
            return;
        }

        const { paymentIntent } = await stripe.retrievePaymentIntent(clientSecret);

        switch (paymentIntent.status) {
            case "succeeded":
                $.ajax({
                    url: "/change-order-status/",
                    headers: {'X-CSRFToken': csrftoken},
                    data: {
                        "order_id": order_id,
                        },
                    type: 'post',
                    success: function(data)
                    {
                        showMessage(data.message);
                    },
                    error: function(error)
                    {
                        showMessage("Something went wrong.");
                    },
                });
                break;
            case "processing":
                showMessage("Your payment is processing.");
                break;
            case "requires_payment_method":
                showMessage("Your payment was not successful, please try again.");
                break;
            default:
                showMessage("Something went wrong.");
                break;
        }
    }

    // ------- UI helpers -------

    function showMessage(messageText) {
        const messageContainer = document.querySelector("#payment-message");
        messageContainer.classList.remove("hidden");
        messageContainer.textContent = messageText;

    }

    // Show a spinner on payment submission
    function setLoading(isLoading) {
        if (isLoading) {
            // Disable the button and show a spinner
            document.querySelector("#submit").disabled = true;
            document.querySelector("#spinner").classList.remove("hidden");
            document.querySelector("#button-text").classList.add("hidden");
        } else {
            document.querySelector("#submit").disabled = false;
            document.querySelector("#spinner").classList.add("hidden");
            document.querySelector("#button-text").classList.remove("hidden");
        }
    }
})
