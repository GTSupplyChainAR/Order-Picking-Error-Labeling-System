import argparse
import json
import utils
from flask import Flask, redirect, render_template, request
from labeling_system import ErrorLabelingManager, ErrorLabelingInstanceContext, SubOrder

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    """
    Gets the index (start) page for the process
    """
    return render_template('index.html')


@app.route('/start-labeling/', methods=['GET'])
def start_labeling():
    """
    Redirects to page of first order to label
    """
    order: SubOrder = manager.get_first_suborder()
    return redirect(f'/error-labeling/task/{order.task_id}/order/{order.order_id}/rack/{order.rack_name}/')


@app.route('/error-labeling/task/<task_id>/order/<order_id>/rack/<rack_name>/', methods=['GET'])
def get_error_labeling_page(task_id, order_id, rack_name):
    """
    Gets the page for labeling errors for this order
    """
    task_id = int(task_id)
    order_id = int(order_id)
    rack_name = str(rack_name)

    order_context: ErrorLabelingInstanceContext = manager.get_order_context(task_id, order_id, rack_name)
    return render_template('error-labeling.html', context=order_context.to_dict())


@app.route('/api/submit-error-labeling/task/<task_id>/order/<order_id>/rack/<rack_name>/', methods=['POST'])
def submit_error_labeling(task_id, order_id, rack_name):
    """
    Submits error labeling and redirects to new page for labeling.
    """
    task_id = int(task_id)
    order_id = int(order_id)
    rack_name = str(rack_name)

    request_data = request.get_json()
    is_order_correct = request_data['isOrderCorrect']

    manager.save_error_labeling(task_id, order_id, rack_name, is_order_correct)

    next_task_id_and_order_id_and_rack_name = manager.get_next_task_id_and_order_id_and_rack_name(task_id, order_id, rack_name)

    if next_task_id_and_order_id_and_rack_name is None:
        return json.dumps({
            'isLabelingComplete': True,
        })

    next_task_id, next_order_id, next_rack_name = next_task_id_and_order_id_and_rack_name
    return json.dumps({
        'isLabelingComplete': False,
        'nextTaskId': next_task_id,
        'nextOrderId': next_order_id,
        'nextRackName': next_rack_name,
    })


@app.route('/labeling-complete/', methods=['GET'])
def labeling_complete():
    return render_template('labeling-complete.html')


@app.template_filter('range')
def template_range(n: int):
    return list(range(n))


if __name__ == '__main__':

    task_pick_paths_file_name = utils.choose_pick_path_file()
    output_log_file_name = utils.choose_output_file()

    # Set up the system manager
    global manager
    manager = ErrorLabelingManager(
        pick_paths_file=task_pick_paths_file_name,
        output_log_file=output_log_file_name,
    )

    # Make the app available to the uesr
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        # Prevent reloading which asks the user for input again
        use_reloader=False,
    )
