from multiprocessing import Queue
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from enum import Enum
from kivy.properties import DictProperty, StringProperty
from lib import TouchSensor, InterfaceManagement
from kivy.core.audio import SoundLoader

Builder.load_file('lib/capturegame.kv')

class GameState(Enum):
    IDLE = 0
    MAIN = 1
    GAME = 2
    EXIT = 3

class MenuScreen(Screen):
    source = StringProperty()
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.source = ''

class CaptureGame(Screen):
    sources = DictProperty({})
    def __init__(self, **kwargs):
        super(CaptureGame, self).__init__(**kwargs)
        self.sources = {}
        self.events = Queue()

    def play_sound(self, item):
        event = ("play_sound", item)
        self.events.put(event)

class CaptureGameFSM(object):
    def __init__(self):
        self.current = GameState.IDLE
        self.game_events = Queue()
        self.capturegame = CaptureGame(name='capture_screen')
        self.touch_sensor = TouchSensor.TouchInput()
        self.capturegame.add_widget(self.touch_sensor)
        self.menuscreen = MenuScreen(name='menu_screen')
        self.external_events = Queue()
        self.internal_events = Queue()
        self.sounds= {}

    def next(self):
        if not self.current == GameState.EXIT:
            if not self.internal_events.empty():
                ev = self.internal_events.get()
                self.dispatch_event(ev)

            if not self.touch_sensor.touch_positions.events.empty():
                ev = self.touch_sensor.touch_positions.events.get()
                self.dispatch_event(ev)

            if not self.capturegame.events.empty():
                ev = self.capturegame.events.get()
                self.dispatch_event(ev)

    def dispatch_event(self, ev):
        event_type = ev[0]
        givens = ev[1:]

        if event_type == "start_game":
            self.start_game()

        if event_type == "stop_game":
            self.stop_game()

        if event_type == "located":
            self.tuio2_located(givens)

        if event_type == "no_located":
            self.no_located()

        if event_type == "capture_item":
            self.capture_item(*givens)

        if event_type == "animals_game" or event_type == "colors_game":
            self.select_game(event_type)

        if event_type == "back_menu":
            self.back_menu()

        if event_type == "play_sound":
            self.play_sound(*givens)

    def start_game(self):
        self.menuscreen.source = 'data/capture_game/icons/menu/menssage.jpg'
        InterfaceManagement.sm.switch_to(self.menuscreen)

    def stop_game(self):
        InterfaceManagement.sm.clear_widgets()

    def play_sound(self, gv):
        item = gv
        sound = SoundLoader.load(self.sounds[item])
        if sound:
            sound.play()

    def back_menu(self):
        self.menuscreen.source = 'data/capture_game/icons/menu/menssage.jpg'
        self.menuscreen.ids.menssage.pos= (0, 100)
        InterfaceManagement.sm.clear_widgets()
        InterfaceManagement.sm.switch_to(self.menuscreen)

    def capture_item(self, it):
        item = 'item_'+ str(int(it[0]))
        self.capturegame.sources[item]= 'data/capture_game/icons/remove_icon.jpg'
        self.play_sound(item)

    def select_game(self, gv):
        game = gv
        if game == "animals_game":
            self.capturegame.sources.update({'wallpaper': 'data/capture_game/wallpapers/animals_wallpaper.jpg',
                                             'item_1': 'data/capture_game/icons/animals/cat_icon.png',
                                             'item_2': 'data/capture_game/icons/animals/dog_icon.png',
                                             'item_3': 'data/capture_game/icons/animals/fish_icon.png',
                                             'item_4': 'data/capture_game/icons/animals/cow_icon.png',
                                             'item_5': 'data/capture_game/icons/animals/tiger_icon.png',
                                             'item_6': 'data/capture_game/icons/animals/bird_icon.png'})

            self.sounds.update({'item_1': 'data/capture_game/sounds/cat_sound.wav',
                                 'item_2': 'data/capture_game/sounds/dog_sound.wav',
                                 'item_3': 'data/capture_game/sounds/fish_sound.wav',
                                 'item_4': 'data/capture_game/sounds/cow_sound.wav',
                                 'item_5': 'data/capture_game/sounds/tiger_sound.wav',
                                 'item_6': 'data/capture_game/sounds/bird_sound.wav'})

            self.menuscreen.source = 'data/capture_game/icons/menu/animals_letters.png'


        if game == "colors_game":
            self.capturegame.sources.update({'wallpaper': 'data/capture_game/wallpapers/colors_wallpaper.jpg',
                                             'item_1': 'data/capture_game/icons/colors/red_icon.jpg',
                                             'item_2': 'data/capture_game/icons/colors/blue_icon.jpg',
                                             'item_3': 'data/capture_game/icons/colors/yellow_icon.jpg',
                                             'item_4': 'data/capture_game/icons/colors/green_icon.jpg',
                                             'item_5': 'data/capture_game/icons/colors/cyan_icon.jpg',
                                             'item_6': 'data/capture_game/icons/colors/magenta_icon.jpg'})

            self.menuscreen.source = 'data/capture_game/icons/menu/colors_letters.png'

        anim = Animation(x=100, y=100, size=(600, 400), t='in_quad', duration=1.)
        anim.bind(on_complete=lambda x, y: InterfaceManagement.sm.switch_to(self.capturegame))
        anim.start(self.menuscreen.ids.menssage)

    def tuio2_located(self, pos):
        event = ("send_data", (b'capture_game', b'located_ok', *pos))
        self.external_events.put(event)

    def no_located(self):
        event = ("send_data", (b'capture_game', b"no_located", *(0, 0, 0, 0)))
        self.external_events.put(event)