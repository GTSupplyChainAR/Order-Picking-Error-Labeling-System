import argparse
import json
from flask import Flask, redirect, render_template, request
from labeling_system import ErrorLabelingManager, ErrorLabelingInstanceContext, Order

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
    order: Order = manager.get_first_order()
    return redirect(f'/error-labeling/task/{order.task_id}/order/{order.order_id}/')


@app.route('/error-labeling/task/<task_id>/order/<order_id>/', methods=['GET'])
def get_error_labeling_page(task_id, order_id):
    """
    Gets the page for labeling errors for this order
    """
    task_id = int(task_id)
    order_id = int(order_id)

    order_context: ErrorLabelingInstanceContext = manager.get_order_context(task_id, order_id)
    return render_template('error-labeling.html', context=order_context.to_dict())


@app.route('/api/submit-error-labeling/task/<task_id>/order/<order_id>/', methods=['POST'])
def submit_error_labeling(task_id, order_id):
    """
    Submits error labeling and redirects to new page for labeling.
    """
    task_id = int(task_id)
    order_id = int(order_id)

    request_data = request.get_json()
    is_order_correct = request_data['isOrderCorrect']

    manager.save_error_labeling(task_id, order_id, is_order_correct)

    next_task_id_and_order_id = manager.get_next_task_id_and_order_id(task_id, order_id)

    if next_task_id_and_order_id is None:
        return json.dumps({
            'isLabelingComplete': True,
        })

    next_task_id, next_order_id = next_task_id_and_order_id
    return json.dumps({
        'isLabelingComplete': False,
        'nextTaskId': next_task_id,
        'nextOrderId': next_order_id
    })


@app.route('/labeling-complete/', methods=['GET'])
def labeling_complete():
    return render_template('labeling-complete.html')


@app.template_filter('range')
def template_range(n: int):
    return list(range(n))


if __name__ == '__main__':

    # Set up the command line argument parser
    parser = argparse.ArgumentParser(description='Run error labeling system used during order-picking studies.')
    parser.add_argument('--task-pick-paths', '-pp', type=str,
                        help='The path to the pick paths JSON file used.')
    parser.add_argument('--output-log-file', '-o', type=str,
                        help='The path to the log file where output will be written.')

    # Parse sys.argv or raise an error
    args = parser.parse_args()

    # Set up the system manager
    global manager
    manager = ErrorLabelingManager(
        pick_paths_file=args.task_pick_paths,
        output_log_file=args.output_log_file,
    )

    # Make the app available to the uesr
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
