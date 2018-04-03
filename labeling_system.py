import json
import os
import datetime
from constants import RACK_NAMES


class SubOrder(object):
    def __init__(self, task_id: int, order_id: int, rack_name: str, source_bins: ['Bin'], receiving_bin_tag: str):
        self.task_id = task_id
        self.order_id = order_id
        self.rack_name = rack_name
        self.source_bins = source_bins
        self.receiving_bin_tag = receiving_bin_tag

        assert self.rack_name in RACK_NAMES
        assert all(bin.bin_tag[0] == rack_name for bin in self.source_bins)


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

    def __init__(self, suborder: SubOrder):
        self.task_id = suborder.task_id
        self.order_id = suborder.order_id
        self.rack_name = suborder.rack_name
        self.receiving_bin_tag = suborder.receiving_bin_tag

        self.expected_items_file_names_and_counts_and_source_bin_tags = []
        for source_bin in suborder.source_bins:  # type: Bin
            self.expected_items_file_names_and_counts_and_source_bin_tags.append((
                f"/static/images/source-bins/{source_bin.bin_tag}.jpg",
                source_bin.number_of_items,
                source_bin.bin_tag,
            ))

    def to_dict(self) -> dict:
        return {
            'task_id': self.task_id,
            'order_id': self.order_id,
            'rack_name': self.rack_name,
            'receiving_bin_tag': self.receiving_bin_tag,
            'expected_items_file_names_and_counts_and_source_bin_tags': self.expected_items_file_names_and_counts_and_source_bin_tags,
        }


class ErrorLabelingManager(object):
    suborders: [SubOrder] = None

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
            self.suborders = self._get_suborders_from_tasks_dict(tasks)

    @staticmethod
    def _get_suborders_from_tasks_dict(tasks_list: [dict]) -> [SubOrder]:
        suborders = []

        for task_dict in tasks_list:
            task_id = task_dict['taskId']
            for rack_name in ['A', 'B']:

                for order_dict in task_dict['orders']:
                    source_bins: [Bin] = []

                    for bin_dict in order_dict['sourceBins']:
                        bin_tag = bin_dict['binTag']
                        if bin_tag[0] == rack_name:
                            source_bins.append(Bin(
                                bin_tag=bin_dict['binTag'],
                                number_of_items=bin_dict['numItems'],
                            ))

                    suborders.append(SubOrder(
                        task_id=task_id,
                        order_id=order_dict['orderId'],
                        rack_name=rack_name,
                        source_bins=source_bins,
                        receiving_bin_tag=order_dict['receivingBinTag']
                    ))

        return suborders

    def get_first_suborder(self) -> SubOrder:
        return self.suborders[0]

    def get_suborder(self, task_id, order_id: int, rack_name: str) -> SubOrder:
        for order in self.suborders:
            if order.task_id == task_id and order.order_id == order_id and order.rack_name == rack_name:
                return order

        raise ValueError(f"Couldn't find order with Task ID {task_id} and Order ID {order_id}.")

    def get_order_context(self, task_id: int, order_id: int, rack_name) -> ErrorLabelingInstanceContext:
        order = self.get_suborder(task_id, order_id, rack_name)
        return ErrorLabelingInstanceContext(order)

    def get_next_task_id_and_order_id_and_rack_name(self, current_task_id: int, current_order_id: int, current_rack_name: str) -> None or (int, int, str):
        for i, order in enumerate(self.suborders):

            if order.task_id == current_task_id and order.order_id == current_order_id and order.rack_name == current_rack_name:
                # Returning None indicates that current_order_id is the last element: i == len(self.orders)
                if i + 1 >= len(self.suborders):
                    return None
                next_order: SubOrder = self.suborders[i + 1]
                return next_order.task_id, next_order.order_id, next_order.rack_name

        raise IndexError(f"Cannot find order with Task ID {current_task_id} and Order ID {current_order_id}")

    def save_error_labeling(self, task_id: int, order_id: int, rack_name: str, is_order_correct: bool) -> None:
        order: SubOrder = self.get_suborder(task_id, order_id, rack_name)

        order_information = {
            'taskId': order.task_id,
            'orderId': order.order_id,
            'rackName': order.rack_name,
            'labelling_time': datetime.datetime.utcnow().isoformat(),
            'is_suborder_correct': is_order_correct,
        }

        with open(self.error_labelling_output_file_path, mode='a') as output_file_pointer:
            output_file_pointer.write(json.dumps(order_information) + "\n")
