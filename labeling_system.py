import json
import os
import datetime


class Order(object):

    subject_id: int = None
    task_id: int = None
    order_id: int = None
    source_bins: ['Bin'] = None
    receiving_bin_tag: str = None

    def __init__(self, subject_id: int, method_id: int, task_id: int, order_id: int, source_bins: ['Bin'], receiving_bin_tag: str):
        self.subject_id = subject_id
        self.method_id = method_id
        self.task_id = task_id
        self.order_id = order_id
        self.source_bins = source_bins
        self.receiving_bin_tag = receiving_bin_tag


class Bin(object):

    bin_tag: str = None
    number_of_items: str = None

    def __init__(self, bin_tag: str, number_of_items: int):
        self.bin_tag = bin_tag
        self.number_of_items = number_of_items


class ErrorLabelingInstanceContext(object):
    """
    Encapsulates all the variables needed for the front-end
    """

    subject_id: int = None
    method_id: int = None
    task_id: int = None
    order_id: int = None

    captured_order_image_file_name: str = None
    expected_items_file_names_and_counts: [(str, int)] = None

    def __init__(self, order: Order):
        self.subject_id = order.subject_id
        self.method_id = order.method_id
        self.task_id = order.task_id
        self.order_id = order.order_id
        self.captured_order_image_file_name = \
            f"/static/images/orders/" \
            f"Subject{self.subject_id:02d}" \
            f"-Method{self.method_id:02d}" \
            f"-Task{self.task_id:02d}" \
            f"-Order{self.order_id:02d}.jpg"

        self.expected_items_file_names_and_counts = []
        for source_bin in order.source_bins:  # type: Bin
            self.expected_items_file_names_and_counts.append((
                f"/static/images/source-bins/{source_bin.bin_tag}.jpg",
                source_bin.number_of_items
            ))

    def to_dict(self) -> dict:
        return {
            'subject_id': self.subject_id,
            'method_id': self.method_id,
            'task_id': self.task_id,
            'order_id': self.order_id,
            'captured_order_image_name': self.captured_order_image_file_name,
            'expected_items_file_names_and_counts': self.expected_items_file_names_and_counts,
        }


class ErrorLabelingManager(object):

    orders: [Order] = None

    error_labelling_output_file_path: str = None

    def __init__(self, json_input_file_path: str, error_labelling_output_file_path: str):

        if not os.path.isfile(json_input_file_path):
            raise OSError(f"Unable to input JSON file: {json_input_file_path}.")

        if not os.path.isfile(error_labelling_output_file_path):
            raise OSError(f"Output log file must exist: {error_labelling_output_file_path}.")

        with open(json_input_file_path, mode='r') as json_file_pointer:
            object_graph = json.load(json_file_pointer)
            self.orders = self._get_orders_from_object_graph(object_graph)

        self.error_labelling_output_file_path = error_labelling_output_file_path

    @staticmethod
    def _get_orders_from_object_graph(object_graph: dict) -> [Order]:
        orders = []

        for subject_dict in object_graph:
            subject_id = subject_dict['subjectId']
            for method_dict in subject_dict['methods']:
                method_id = method_dict['methodId']
                for task_dict in method_dict['tasks']:
                    task_id = task_dict['taskId']
                    for order_dict in task_dict['orders']:

                        source_bins: [Bin] = []

                        for bin_dict in order_dict['sourceBins']:
                            source_bins.append(Bin(
                                bin_tag=bin_dict['binTag'],
                                number_of_items=bin_dict['numItems'],
                            ))

                        orders.append(Order(
                            subject_id=subject_id,
                            method_id=method_id,
                            task_id=task_id,
                            order_id=order_dict['orderId'],
                            source_bins=source_bins,
                            receiving_bin_tag=order_dict['receivingBinTag']
                        ))

        return orders

    def get_first_order_id(self) -> int:
        return self.orders[0].order_id

    def get_order(self, order_id: int) -> Order:
        for order in self.orders:
            if order.order_id == order_id:
                return order

        raise ValueError(f"Couldn't find order with ID {order_id}.")

    def get_order_context(self, order_id: int) -> ErrorLabelingInstanceContext:
        order = self.get_order(order_id)
        return ErrorLabelingInstanceContext(order)

    def get_next_order_id(self, current_order_id: int) -> int:
        for i, order in enumerate(self.orders):

            if order.order_id == current_order_id:
                # Returning None indicates that current_order_id is the last element: i == len(self.orders)
                return self.orders[i + 1].order_id if i + 1 < len(self.orders) else None

        raise IndexError(f"Cannot find order with id {current_order_id}")

    def save_error_labeling(self, order_id: int, is_order_correct: bool) -> None:
        order: Order = self.get_order(order_id)

        order_information = ErrorLabelingInstanceContext(order).to_dict()
        order_information['labelling_time'] = datetime.datetime.utcnow().isoformat()
        order_information['is_order_correct'] = is_order_correct

        with open(self.error_labelling_output_file_path, mode='a') as output_file_pointer:
            output_file_pointer.write(json.dumps(order_information) + "\n")