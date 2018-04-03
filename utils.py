import os
import logging


def choose_pick_path_file():
    """ Interacts with the console so the user can select a pick path to run. """
    study_folders_path = os.path.join(
        '.',
        'data',
        'RFID-Study-Task-Generation',
        'output',
    )

    file_number_to_file = {}
    i = 1
    print('Choose from the files below:')

    # Iterate through all folders and pick path files
    for folder_name in os.listdir(study_folders_path):
        folder_path = os.path.join(study_folders_path, folder_name)
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            # Display the option
            print('%-3d %s' % (i, file_name))

            # Register the file path for the printed file name
            file_number_to_file[i] = file_path

            i += 1

    print()  # newline

    print('What file would you like to select?')
    file_id = int(input('> (#) '))

    # Look up the file path by the file_id and return
    file_path_selected = file_number_to_file[file_id]

    print()  # newline

    print('Is this the file you selected?')
    print(file_path_selected)
    confirmation = input('> (y/n) ')

    if confirmation != 'y':
        raise SystemExit('Incorrect file selected.')

    return file_path_selected


def choose_output_file():
    """ Interacts with the console so the user can choose an output logfile. """

    print()  # newline

    print('What output file would you like to write to?')
    output_file_name = input('> ')

    print()  # newline

    return output_file_name


def configure_logger(logger, level=logging.DEBUG):
    """ Configures the given logger to print messages at the given level. """
    logger.setLevel(level)
    loggerHandler = logging.StreamHandler()
    loggerFormatter = logging.Formatter('%(asctime)-20s : %(name)-14s : %(levelname)-8s : %(message)s')
    loggerHandler.setFormatter(loggerFormatter)
    loggerHandler.setLevel(level)
    logger.addHandler(loggerHandler)
    return logger
