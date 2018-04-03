import json
import os
import datetime


class Order(object):
    def __init__(self, task_id: int, order_id: int, source_bins: ['Bin'], receiving_bin_tag: str):
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

    def __init__(self, order: Order):
        self.task_id = order.task_id
        self.order_id = order.order_id
        self.receiving_bin_tag = order.receiving_bin_tag

        self.expected_items_file_names_and_counts_and_source_bin_tags = []
        for source_bin in order.source_bins:  # type: Bin
            self.expected_items_file_names_and_counts_and_source_bin_tags.append((
                f"/static/images/source-bins/{source_bin.bin_tag}.jpg",
                source_bin.number_of_items,
                source_bin.bin_tag,
            ))

    def to_dict(self) -> dict:
        return {
            'task_id': self.task_id,
            'order_id': self.order_id,
            'receiving_bin_tag': self.receiving_bin_tag,
            'expected_items_file_names_and_counts_and_source_bin_tags': self.expected_items_file_names_and_counts_and_source_bin_tags,
        }


class ErrorLabelingManager(object):
    orders: [Order] = None

    error_labelling_output_file_path: str = None

    def __init__(self, pick_paths_file: str, output_log_file: str):

        if not os.path.isfile(pick_paths_file):
            raise OSError(f"Unable to input JSON file: {pick_paths_file}.")

        if not os.path.isfile(output_log_file):
            with open(output_log_file, "w+"):
                # Create the file
                pass

        self.error_labelling_output_file_path = output_log_file

        with open(pick_paths_file, mode='r') as json_file_pointer:
            obj = json.load(json_file_pointer)
            tasks = obj['tasks']
            self.orders = self._get_orders_from_tasks_dict(tasks)

    @staticmethod
    def _get_orders_from_tasks_dict(tasks_list: [dict]) -> [Order]:
        orders = []

        for task_dict in tasks_list:
            task_id = task_dict['taskId']
            for order_dict in task_dict['orders']:

                source_bins: [Bin] = []

                for bin_dict in order_dict['sourceBins']:
                    source_bins.append(Bin(
                        bin_tag=bin_dict['binTag'],
                        number_of_items=bin_dict['numItems'],
                    ))

                orders.append(Order(
                    task_id=task_id,
                    order_id=order_dict['orderId'],
                    source_bins=source_bins,
                    receiving_bin_tag=order_dict['receivingBinTag']
                ))

        return orders

    def get_first_order(self) -> Order:
        return self.orders[0]

    def get_order(self, task_id, order_id: int) -> Order:
        for order in self.orders:
            if order.task_id == task_id and order.order_id == order_id:
                return order

        raise ValueError(f"Couldn't find order with Task ID {task_id} and Order ID {order_id}.")

    def get_order_context(self, task_id: int, order_id: int) -> ErrorLabelingInstanceContext:
        order = self.get_order(task_id, order_id)
        return ErrorLabelingInstanceContext(order)

    def get_next_task_id_and_order_id(self, current_task_id: int, current_order_id: int) -> None or (int, int):
        for i, order in enumerate(self.orders):

            if order.task_id == current_task_id and order.order_id == current_order_id:
                # Returning None indicates that current_order_id is the last element: i == len(self.orders)
                if i + 1 >= len(self.orders):
                    return None
                next_order: Order = self.orders[i + 1]
                return next_order.task_id, next_order.order_id

        raise IndexError(f"Cannot find order with Task ID {current_task_id} and Order ID {current_order_id}")

    def save_error_labeling(self, task_id: int, order_id: int, is_order_correct: bool) -> None:
        order: Order = self.get_order(task_id, order_id)

        order_information = {
            'taskId': order.task_id,
            'orderId': order.order_id,
            'labelling_time': datetime.datetime.utcnow().isoformat(),
            'is_order_correct': is_order_correct,
        }

        with open(self.error_labelling_output_file_path, mode='a') as output_file_pointer:
            output_file_pointer.write(json.dumps(order_information) + "\n")
