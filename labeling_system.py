import json
import os
import datetime


class Bin(object):
    bin_tag: str = None
    number_of_items: str = None

    def __init__(self, bin_tag: str, number_of_items: int):
        self.bin_tag = bin_tag
        self.number_of_items = number_of_items


class Order(object):
    def __init__(self,
                 subject_id: int,
                 method_number: int,
                 method_id: str,
                 task_id: int,
                 task_number: int,
                 order_id: int,
                 source_bins: [Bin],
                 receiving_bin_tag: str):
        self.subject_id = subject_id
        self.method_number = method_number
        self.method_id = method_id.replace('/', '-')
        self.task_id = task_id
        self.task_number = task_number
        self.order_id = order_id
        self.source_bins = source_bins
        self.receiving_bin_tag = receiving_bin_tag

    @property
    def receiving_bin_image_index_in_task_directory(self):
        return int(self.receiving_bin_tag[-1]) - 1

    @property
    def actual_bin_file_path(self):
        folder_path = os.path.join(
            'static',
            'images',
            'By subject, testing, sorted',
            f'Subject {self.subject_id:02d}',
            f'Testing',
            f'Method n{self.method_number} ({self.method_id})',
            f'Task n{self.task_number:02d}',
        )

        files_in_task_image_directory = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), folder_path))
        files_in_task_image_directory = [file for file in files_in_task_image_directory if file.endswith('JPG')]
        files_in_task_image_directory = sorted(files_in_task_image_directory)

        receiving_bin_image_name = files_in_task_image_directory[self.receiving_bin_image_index_in_task_directory]

        return '/' + os.path.join(folder_path, receiving_bin_image_name)

    def to_dict(self) -> dict:

        # Create an array to hold the information about the source bins from which we expect to see items
        expected_items_file_names_and_counts_and_source_bin_tags = []
        for source_bin in self.source_bins:  # type: Bin
            expected_items_file_names_and_counts_and_source_bin_tags.append((
                f"/static/images/source-bins/{source_bin.bin_tag}.jpg",
                source_bin.number_of_items,
                source_bin.bin_tag,
            ))

        return {
            'subject_id': self.subject_id,
            'method_id': self.method_id,
            'method_number': self.method_number,
            'task_id': self.task_id,
            'task_number': self.task_number,
            'order_id': self.order_id,
            'actual_bin_file_path': self.actual_bin_file_path,
            'receiving_bin_tag': self.receiving_bin_tag,
            'expected_items_file_names_and_counts_and_source_bin_tags': expected_items_file_names_and_counts_and_source_bin_tags,
        }


class ErrorLabelingManager(object):
    orders: [Order] = None

    error_labelling_output_file_path: str = None

    def __init__(self, subjects_file: str, output_log_file: str):

        if not os.path.isfile(subjects_file):
            raise OSError(f"Unable to input JSON file: {subjects_file}.")

        if not os.path.isfile(output_log_file):
            with open(output_log_file, "w+"):
                # Create the file
                pass

        self.error_labelling_output_file_path = output_log_file

        with open(subjects_file, mode='r') as json_file_pointer:
            obj = json.load(json_file_pointer)
            subjects_list = obj['subjects']
            self.orders = self._get_orders_from_subjects_list(subjects_list)

    def _get_orders_from_subjects_list(self, subjects_list: [dict]) -> [Order]:
        orders = []

        for subject_dict in subjects_list:
            subject_id = subject_dict['subjectId']

            for method_i, method_dict in enumerate(subject_dict['methods']):
                method_number = method_i + 1

                method_id = method_dict['methodId']

                for task_i, task_dict in enumerate(method_dict['tasks']):
                    task_number = task_i + 1

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
                            method_number=method_number,
                            task_id=task_id,
                            task_number=task_number,
                            order_id=order_dict['orderId'],
                            source_bins=source_bins,
                            receiving_bin_tag=order_dict['receivingBinTag']
                        ))

        return orders

    def get_first_order(self) -> Order:
        return self.orders[0]

    def get_order(self, subject_id: int, method_id: str, task_id, order_id: int) -> Order:
        for order in self.orders:
            if order.subject_id == subject_id \
                    and order.method_id == method_id \
                    and order.task_id == task_id \
                    and order.order_id == order_id:
                return order

        raise ValueError(f"Couldn't find order")

    def get_next_order(self, current_order: Order) -> None or Order:
        for i, order in enumerate(self.orders):

            if order.subject_id == current_order.subject_id \
                    and order.method_id == current_order.method_id \
                    and order.task_id == current_order.task_id \
                    and order.order_id == current_order.order_id:
                # Returning None indicates that current_order_id is the last element: i == len(self.orders)
                if i + 1 >= len(self.orders):
                    return None
                next_order: Order = self.orders[i + 1]
                return next_order

        raise ValueError()

    def save_error_labeling(self, order: Order, is_order_correct: bool) -> None:

        order_information = {
            'subjectId': order.subject_id,
            'taskId': order.task_id,
            'methodId': order.method_id,
            'orderId': order.order_id,
            'labelling_time': datetime.datetime.utcnow().isoformat(),
            'is_order_correct': is_order_correct,
        }

        with open(self.error_labelling_output_file_path, mode='a') as output_file_pointer:
            output_file_pointer.write(json.dumps(order_information) + "\n")
