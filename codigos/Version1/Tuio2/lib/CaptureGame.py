from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import NumericProperty, DictProperty, StringProperty
from multiprocessing import Queue
from lib import InterfaceManagement

Builder.load_file('lib/capturegame.kv')

class ItemScreen(Screen):
    source = StringProperty()
    def __init__(self, **kwargs):
        super(ItemScreen, self).__init__(**kwargs)
        self.source = ''

class CaptureMenu(Screen):
    def __init__(self, **kwargs):
        super(CaptureMenu, self).__init__(**kwargs)
        self.events = Queue()

class MenssageScreen(Screen):
    pass

class CaptureGameFSM(object):
    def __init__(self):
        self.internal_events = Queue()
        self.external_events = Queue()
        self.capturegame = CaptureScreen(name='capture_game')
        self.capturemenu = CaptureMenu(name='capture_menu')
        self.capturemenssage = MenssageScreen(name='menssage_screen')
        self.capturemenssage.ids.home_button.bind(on_press= lambda x: self.stop_game())

    def next(self):

        if not self.capturemenu.events.empty():
            ev = self.capturemenu.events.get()
            self.dispatch_event(ev)

        if not self.capturegame.events.empty():
            ev = self.capturegame.events.get()
            self.dispatch_event(ev)

        if not self.internal_events.empty():
            ev = self.internal_events.get()
            self.dispatch_event(ev)


    def dispatch_event(self, ev):
        event_type = ev[0]
        givens = ev[1:]

        if event_type == "start_game":
            self.start_game()

        if event_type == "stop_game":
            self.stop_game()

        if event_type == "select_game":
            self.select_game(*givens)

        if event_type == "located_ok":
            self.located_ok(givens)

        if event_type == "no_located":
            self.no_located()

        if event_type == "back_menu":
            self.back_menu()

        if event_type == "capture_item":
            self.capture_item(givens[0])

    def capture_item(self, it):
        item = it
        itemscreen = ItemScreen()
        itemscreen.source = self.capturegame.sources[item]
        self.capturegame.sources[item] = 'data/capture_game/icons/remove_icon.jpg'
        event = ("send_data",(b'capture_game' , b'capture_item', *(int(item[5]), 0, 0, 0)))
        self.external_events.put(event)
        InterfaceManagement.sm.clear_widgets()
        InterfaceManagement.sm.switch_to(itemscreen)

    def back_menu(self):
        InterfaceManagement.sm.clear_widgets()
        InterfaceManagement.sm.switch_to(self.capturemenu)
        event = ("send_data", (b'capture_game', b"back_menu", *(0, 0, 0, 0)))
        self.external_events.put(event)

    def no_located(self):
        InterfaceManagement.sm.clear_widgets()
        InterfaceManagement.sm.switch_to(self.capturemenssage)

    def located_ok(self, gv):
        InterfaceManagement.sm.clear_widgets()
        InterfaceManagement.sm.switch_to(self.capturegame)
        pos = gv[0]
        self.capturegame.trasl_x = pos[0] * (-1)
        self.capturegame.trasl_y = pos[1] * (-1)
        self.capturegame.scale_x = 1.66
        self.capturegame.angle = pos[2]

    def start_game(self):
        InterfaceManagement.sm.clear_widgets()
        InterfaceManagement.sm.switch_to(self.capturemenu)

    def stop_game(self):
        InterfaceManagement.sm.clear_widgets()
        event = ("stop_game", "capture_game", "")
        self.external_events.put(event)

    def select_game(self, gv):
        game = gv

        if game == "animals_game":
            self.capturegame.sources.update({'wallpaper': 'data/capture_game/wallpapers/animals_wallpaper.jpg',
                                            'item_1':'data/capture_game/icons/animals/cat_icon.png',
                                            'item_2':'data/capture_game/icons/animals/dog_icon.png',
                                            'item_3':'data/capture_game/icons/animals/fish_icon.png',
                                            'item_4':'data/capture_game/icons/animals/cow_icon.png',
                                            'item_5':'data/capture_game/icons/animals/tiger_icon.png',
                                            'item_6':'data/capture_game/icons/animals/bird_icon.png'})

            event = ("send_data", (b'capture_game', b"animals_game", *(0, 0, 0, 0)))
            self.external_events.put(event)

        if game == "colors_game":
            self.capturegame.sources.update({'wallpaper': 'data/capture_game/wallpapers/colors_wallpaper.jpg',
                                             'item_1': 'data/capture_game/icons/colors/red_icon.jpg',
                                             'item_2': 'data/capture_game/icons/colors/blue_icon.jpg',
                                             'item_3': 'data/capture_game/icons/colors/yellow_icon.jpg',
                                             'item_4': 'data/capture_game/icons/colors/green_icon.jpg',
                                             'item_5': 'data/capture_game/icons/colors/cyan_icon.jpg',
                                             'item_6': 'data/capture_game/icons/colors/magenta_icon.jpg'})

            event = ("send_data", (b'capture_game', b"colors_game", *(0, 0, 0, 0)))
            self.external_events.put(event)

        InterfaceManagement.sm.switch_to(self.capturemenssage)

class CaptureScreen(Screen):
    trasl_x = NumericProperty()
    trasl_y = NumericProperty()
    scale_x = NumericProperty()
    scale_y = NumericProperty()
    angle = NumericProperty()
    sources = DictProperty({})

    def __init__(self, **kwargs):
        super(CaptureScreen, self).__init__(**kwargs)
        self.trasl_x = 0
        self.trasl_y = 0
        self.scale_x = 5/3
        self.scale_y = 3/2
        self.angle = 0
        self.sources = {}
        self.events = Queue()

    def capture_item(self, it):
        item = it
        event = ("capture_item", item, "")
        self.events.put(event)

    def back_menu(self):
        event = ("back_menu", "")
        self.events.put(event)




