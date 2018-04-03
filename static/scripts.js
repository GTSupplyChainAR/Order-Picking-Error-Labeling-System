$(document).ready(function () {

    function submitErrorLabeling(taskId, orderId, rackName, isOrderCorrect) {
        console.log(taskId, orderId, rackName, isOrderCorrect);

        return $.ajax({
            url: '/api/submit-error-labeling/task/' + taskId + '/order/' + orderId + '/rack/' + rackName + '/',
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
                handleSuccessAndMoveForward(data.nextTaskId, data.nextOrderId, data.nextRackName);
            }
        }).fail(handleServerError);
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

    function handleSuccessAndMoveForward(nextTaskId, nextOrderId, nextRackName) {
        $("<div/>", {
            class: 'alert alert-success',
            role: 'alert',
            text: 'Saved information! Moving to Task ID ' + nextTaskId + ' and Order ID ' + nextOrderId + ' now with rack ' + nextRackName + '.',
        }).appendTo("#confirmation-messages");

        setTimeout(function () {
            window.location = '/error-labeling/task/' + nextTaskId + '/order/' + nextOrderId + '/rack/' + nextRackName;
        }, 1000);
    }

    function handleServerError() {
        $("<div/>", {
            class: 'alert alert-danger',
            role: 'alert',
            text: 'Failed to save information for order ID ' + orderId,
        }).appendTo("#confirmation-messages");
    }

    var taskId = $("#task-id").val();
    var orderId = $("#order-id").val();
    var rackName = $("#rack-name").val();

    $("#button-yes").click(function () {
        submitErrorLabeling(taskId, orderId, rackName, /* isOrderCorrect: */ true);
    });

    $("#button-no").click(function () {
        submitErrorLabeling(taskId, orderId, rackName, /* isOrderCorrect: */ false);
    });

    $(document).keypress(function (e) {
        if (e.which === 121) {  // 'Y' was pressed
            submitErrorLabeling(taskId, orderId, rackName, true);
        } else if (e.which === 110) {  // 'N' was pressed
            submitErrorLabeling(taskId, orderId, rackName, false);
        }
    });

});
