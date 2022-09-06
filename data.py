from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from json import dumps
from os.path import join
from time import time
from uuid import uuid4
import csv


class DataLogger:

    url = 'xxxxxxxxxxxxxxxx'  # censored -- change as needed (firebase URL), or save files locally.
    user_id = uuid4()
    t0 = time()
    online_data_packet = {'-1': {}}
    local_data_packet = []
    question_number = -1

    def __init__(self, online=False):
        self.online = online
        self.peek_amount = 0
        self.correct_amount = 0
        self.question_number = -1
        self.total_question_time = 0
        self.question_start_time = 0
        self.solution_number = 0

    class TimeStamp:

        def __init__(self, event_type, *args):
            self.event_type = event_type
            self.args = args

        def __call__(self, function):
            """
            The TimeStamp class is used as a class decorator. A timestamp is created by subtracting the current time by
            t0. Then data is added to the numerically largest key in the DataLogger dictionary.
            :param function: The function to be called
            """

            def wrapper(*args, **kwargs):
                time_log = "%.5f" % (time() - DataLogger.t0)
                result = function(*args, **kwargs)
                if log.online:
                    time_log = time_log.replace('.', ',')  # Firebase doesn't allow decimal points.
                    # question_number = max(DataLogger.online_data_packet, key=int)
                    if result is not None:
                        DataLogger.online_data_packet[str(log.question_number)].update({time_log: {self.event_type: result}})
                    else:
                        DataLogger.online_data_packet[str(log.question_number)].update({time_log: self.event_type})
                else:
                    DataLogger.local_data_packet.append([time_log, log.question_number, self.event_type, result])

                if self.event_type == 'peek':  # Keeps an internal record on the number of peeks
                    log.peek_amount += 1
                elif self.event_type == 'solution':  # Keeps an internal record on the number of correct responses
                    for event_data in result.values():
                        if event_data['correct']:
                            log.correct_amount += 1
                    log.solution_number += 1
                    if log.solution_number % 5 == 0: # Avoids updating the time per question 5 times (one for each response field)
                        log.total_question_time += float(time_log) - log.question_start_time
                elif self.event_type == 'next':  # Keeps an internal record of the time spent per question
                    log.question_start_time = float(time_log)
            return wrapper

    def save_data(self, *args):
        if self.online:
            UrlRequest(url=f"{self.url}/{self.user_id}.json", req_body=dumps(self.online_data_packet), method='PATCH')
        else:
            file_path = join(App.get_running_app().user_data_dir, f'{self.user_id}-data.csv')
            with open(file_path, 'w') as data_file:
                csv_writer = csv.writer(data_file)
                csv_writer.writerows(self.local_data_packet)

log = DataLogger()

# TODO: Make sure that the data logger can easily be switched to online. At the moment it is always set to False.
