$(document).ready(function () {

    var subjectId = $("#subject-id").val();
    var methodId = $("#method-id").val();
    var taskId = $("#task-id").val();
    var orderId = $("#order-id").val();

    function submitErrorLabeling(isOrderCorrect) {
        console.log(isOrderCorrect);

        return $.ajax({
            url: '/api/submit-error-labeling/subject/' + subjectId + '/method/' + methodId + '/task/' + taskId + '/order/' + orderId + '/',
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
                handleSuccessAndMoveForward(data.nextSubjectId, data.nextMethodId, data.nextTaskId, data.nextOrderId);
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

    function handleSuccessAndMoveForward(nextSubjectId, nextMethodId, nextTaskId, nextOrderId) {
        $("<div/>", {
            class: 'alert alert-success',
            role: 'alert',
            text: 'Saved information! Moving on now.',
        }).appendTo("#confirmation-messages");

        setTimeout(function () {
            window.location = '/error-labeling/subject/' + nextSubjectId + '/method/' + nextMethodId +'/task/' + nextTaskId + '/order/' + nextOrderId + '/';
        }, 1000);
    }

    function handleServerError() {
        $("<div/>", {
            class: 'alert alert-danger',
            role: 'alert',
            text: 'Failed to save information for order ID ' + orderId,
        }).appendTo("#confirmation-messages");
    }

    $("#button-yes").click(function () {
        submitErrorLabeling(/* isOrderCorrect: */ true);
    });

    $("#button-no").click(function () {
        submitErrorLabeling(/* isOrderCorrect: */ false);
    });

    $(document).keypress(function (e) {
        if (e.which === 121) {  // 'Y' was pressed
            submitErrorLabeling(/* isOrderCorrect: */ true);
        } else if (e.which === 110) {  // 'N' was pressed
            submitErrorLabeling(/* isOrderCorrect: */ false);
        }
    });

});
