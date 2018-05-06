import argparse
import json
import utils
from flask import Flask, redirect, render_template, request
from labeling_system import ErrorLabelingManager, Order

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


@app.route('/error-labeling/subject/<subject_id>/task/<task_id>/order/<order_id>/', methods=['GET'])
def get_error_labeling_page(subject_id, task_id, order_id):
    """
    Gets the page for labeling errors for this order
    """
    subject_id = int(subject_id)
    task_id = int(task_id)
    order_id = int(order_id)

    order: Order = manager.get_order(subject_id, task_id, order_id)
    return render_template('error-labeling.html', context=order.to_dict())


@app.route('/api/submit-error-labeling/subject/<subject_id>/task/<task_id>/order/<order_id>/', methods=['POST'])
def submit_error_labeling(subject_id, task_id, order_id):
    """
    Submits error labeling and redirects to new page for labeling.
    """
    subject_id = int(subject_id)
    task_id = int(task_id)
    order_id = int(order_id)

    request_data = request.get_json()
    is_order_correct = request_data['isOrderCorrect']

    order = manager.get_order(subject_id, task_id, order_id)
    manager.save_error_labeling(order, is_order_correct)

    next_order = manager.get_next_order(order)

    if next_order is None:
        return json.dumps({
            'isLabelingComplete': True,
        })

    return json.dumps({
        'isLabelingComplete': False,
        'nextSubjectId': next_order.subject_id,
        'nextTaskId': next_order.task_id,
        'nextOrderId': next_order.order_id,
    })


@app.route('/labeling-complete/', methods=['GET'])
def labeling_complete():
    return render_template('labeling-complete.html')


@app.template_filter('range')
def template_range(n: int):
    return list(range(n))


if __name__ == '__main__':

    subjects_file_name = './data/subjects.json'
    output_log_file_name = utils.choose_output_file()

    # Set up the system manager
    global manager
    manager = ErrorLabelingManager(
        subjects_file=subjects_file_name,
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
