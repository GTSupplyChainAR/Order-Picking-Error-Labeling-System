import sys
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
    order_id: int = manager.get_first_order_id()
    return redirect(f'/error-labeling/{order_id}')


@app.route('/error-labeling/<order_id>/', methods=['GET'])
def get_error_labeling_page(order_id):
    """
    Gets the page for labeling errors for this order
    """
    order_id = int(order_id)
    order_context: ErrorLabelingInstanceContext = manager.get_order_context(order_id)
    return render_template('error-labeling.html', context=order_context.to_dict())


@app.route('/api/submit-error-labeling/<order_id>/', methods=['POST'])
def submit_error_labeling(order_id):
    """
    Submits error labeling and redirects to new page for labeling.
    """
    order_id = int(order_id)

    request_data = request.get_json()
    is_order_correct = request_data['isOrderCorrect']

    manager.save_error_labeling(order_id, is_order_correct)

    next_order_id = manager.get_next_order_id(order_id)

    if next_order_id is None:
        return json.dumps({
            'isLabelingComplete': True,
            'nextOrderId': -1
        })

    return json.dumps({
        'isLabelingComplete': False,
        'nextOrderId': next_order_id
    })


@app.route('/labeling-complete/', methods=['GET'])
def labeling_complete():
    return render_template('labeling-complete.html')


@app.template_filter('range')
def template_range(n: int):
    return list(range(n))


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print(sys.argv)
        print("python app.py json_input_file_path error_labeling_output_file_path")
        exit(1)

    global manager
    manager = ErrorLabelingManager(
        json_input_file_path=sys.argv[1],
        error_labelling_output_file_path=sys.argv[2],
    )

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
