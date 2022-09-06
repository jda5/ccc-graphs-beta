from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import BooleanProperty
from data import log
from time import time
from widgets import ConnectionPopup
from kivy.clock import Clock

class Manager(ScreenManager):
    pass


class HomeScreen(Screen):

    def on_enter(self, *args):
        popup = ConnectionPopup()
        if not popup.connection():
            Clock.schedule_once(lambda dt: popup.open())


class CCCScreen(Screen):
    question_number = -1

    @log.TimeStamp('ccc-task-started')
    def on_enter(self, *args):
        self.ids['_navigation'].update_question()
        log.question_start_time = time() - log.t0

class CompletionScreen(Screen):

    def on_pre_enter(self, *args):
        score = self.manager.get_screen('ccc_screen').ids['_navigation'].score
        self.ids['score'].text = str(score)


class TutorialScreen(Screen):

    def on_enter(self, *args):
        for i, response_field in enumerate(self.ids['response_fields'].children):
            # response_field.ids['expression_writer'].draw()
            response_field.reset_field()
            if i < 3:
                response_field.switch_mode()
        self.ids['_navigation'].ids['compare'].disabled = True

class InfoScreen(Screen):

    def on_pre_enter(self, *args):
        ccc_screen = self.manager.get_screen('ccc_screen')
        self.ids['score_info'].text = str(ccc_screen.ids['_navigation'].score)
        self.ids['peek_info'].text = str(log.peek_amount // 2)
        self.ids['correct_info'].text = str(log.correct_amount)
        self.ids['time_info'].text = str(int(log.total_question_time / ((ccc_screen.question_number + 1) * 5)))
        # Need to add one to the question number because of the 0-indexing
