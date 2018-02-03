$(document).ready(function () {

    function submitErrorLabeling(orderId, isOrderCorrect) {
        console.log(orderId, isOrderCorrect);

        return $.ajax({
            url: '/api/submit-error-labeling/' + orderId + '/',
            method: 'POST',
            data: JSON.stringify({
                isOrderCorrect: isOrderCorrect,
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
        }).done(function (data) {
            if (data.isLabelingComplete) {
                handleLabelingComplete();
            } else {
                handleSuccessAndMoveForward(data.nextOrderId);
            }
        }).fail(handleError);
    }

    function handleLabelingComplete() {
        $("<div/>", {
            class: 'alert alert-success',
            role: 'alert',
            text: 'Saved information for order ID ' + orderId + '! Done labeling orders!',
        }).appendTo("#confirmation-messages");

        setTimeout(function () {
            window.location = '/labeling-complete/';
        }, 500)
    }

    function handleSuccessAndMoveForward(nextOrderId) {
        $("<div/>", {
            class: 'alert alert-success',
            role: 'alert',
            text: 'Saved information for order ID ' + orderId + '! Moving to order ID ' + nextOrderId + ' now.',
        }).appendTo("#confirmation-messages");

        setTimeout(function () {
            window.location = '/error-labeling/' + nextOrderId + '/';
        }, 500);
    }

    function handleError() {
        $("<div/>", {
            class: 'alert alert-danger',
            role: 'alert',
            text: 'Failed to save information for order ID ' + orderId,
        }).appendTo("#confirmation-messages");
    }

    var orderId = $("#order-id").val();

    $("#button-yes").click(function () {
        submitErrorLabeling(orderId, true);
    });

    $("#button-no").click(function () {
        submitErrorLabeling(orderId, false);
    });

    $(document).keypress(function (e) {
        if (e.which === 121) {  // 'Y' was pressed
            submitErrorLabeling(orderId, true);
        } else if (e.which === 110) {  // 'N' was pressed
            submitErrorLabeling(orderId, false);
        }
    });

});
