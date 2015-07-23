
from __future__ import print_function


__author__ = 'vsp'
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Color,Rectangle,Triangle
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.vector import Vector
import random,time

from collections import defaultdict

def merge_dicts(old_dict,new_dict):
    '''
    Merges two dictionaries. Overwrites old values with new ones.
    :param old_dict: dict
    :param new_dict: dict
    :return: dict
    '''
    return_dict = old_dict.copy()
    return_dict.update(new_dict)
    return return_dict

def merge_iters(old_iter,new_iter):
    '''
    Merges two iterables.
    :param old_iter:
    :param new_iter:
    :return:
    '''
    return old_iter + new_iter


class Timer(object):
    '''
    debugging purposes, found the timer. Just put the material in a with block
    (e.g. "with Timer() as time:")   and it will tell you automatically when the code finishes
    '''
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.start = time.time()

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, value, exc_traceback):
        name = ''
        if self.name:
            name = str(self.name)
        print(name, 'Elapsed: ', repr(time.time() - self.start), 'secs.')


class KwCleanUp(object):
    '''
    A class that, depending on if a keyword
    argument is within a defined set, will store that value
    and pop it from the dictionary. Useful for variable cleanup.
    '''
    desired_attributes = ()
    def __init__(self,**kwargs):
        for arg in kwargs:
            if arg in self.desired_attributes:
                setattr(self,arg,
                        kwargs.pop(arg,None)
                        )

class ChangeableBoxLayoutKwCleanup(KwCleanUp):
    desired_kept_attributes = (
        'no_repeated_classes',
        'repeated_class_args',
        'repeated_classes_kwargs',
        'extra_classes_args',
        'extra_classes_kwargs',
    )



class ChangeableBoxLayout(BoxLayout):
    repeated_class = Widget
    repeated_class_kwargs = {}
    repeated_class_args = ()
    no_repeated_classes = 4
    extra_classes = ()
    extra_classes_kwargs = defaultdict(tuple)
    extra_classes_args = defaultdict(dict)

    desired_kept_vars = ()

    desired_init_vars = (
                        'no_repeated_classes',
                        'repeated_class_args',
                        'repeated_class_kwargs',
                        'extra_classes_args',
                        'extra_classes_kwargs',
                        )

    map_kept_attrs = {}

    bg_color = 0,0,0
    bg_color_args = {'mode':'hsv'}

    def __init__(self, no_repeated_classes=None,
                  repeated_class_args = (),repeated_class_kwargs=None,
                  extra_classes_args = None,extra_classes_kwargs=None,
                 bg_color = None, bg_color_args = None,
                **kwargs):
        if bg_color_args is None:
            bg_color_args = {}

        self.touch_coords = None

        self.process_inputs_against_class_instances(
                                               no_repeated_classes,
                                               repeated_class_args,
                                               repeated_class_kwargs,
                                               extra_classes_args,
                                               extra_classes_kwargs,
                                               kwargs
                                                )

        # Now, run the ChangeableBoxLayout initiation.
        # Don't break built-in functionality.
        super(ChangeableBoxLayout,self).__init__(**kwargs)


        self.setup_background(bg_color,bg_color_args)

        ## possibly implement error checking for arguments, but it's non-trivial.
        ## if you get an error from here,
        ## it's likely because your lists do not match up.
        self.rpt_widgets = []
        self.add_repeated_class_widgets()

        self.extra_widgets = []
        self.add_extra_classes()

        self.ready_for_update = False

    def setup_background(self,bg_color,bg_color_args):
        background = bg_color if bg_color else self.bg_color
        bg_kwargs = self.bg_color_args.copy()
        bg_kwargs.update(bg_color_args)

        with self.canvas.before:
            Color(*background,**bg_kwargs)
            self.rect = Rectangle(size = self.size,pos=self.pos)

        self.bind(size=self._update_rect,pos = self._update_rect)

    def add_repeated_class_widgets(self):

        #first add all of the repeated class elements
        for i in range(self.times_rpt_class):
            # noinspection PyArgumentList
            class_instance =self.single_rpt_class()

            self.add_widget(class_instance)
            self.rpt_widgets.append(class_instance)

    def single_rpt_class(self):
        return self.repeated_class(
                            *self.rpt_args,**self.rpt_kwargs
                            )

    def add_extra_classes(self):
         #then add all of the extra class elements, with desired arguments
        for extra_class in self.extra_classes:
            self.add_widget(extra_class(
                *self.extra_args[extra_class],
                **self.extra_kwargs[extra_class]
                )
            )



    def process_inputs_against_class_instances(self,
                                               no_repeated_classes,
                                               repeated_class_args,
                                               repeated_class_kwargs,
                                               extra_classes_args,
                                               extra_classes_kwargs,
                                               kwargs
                                                ):
        # If we need to do anything special with the inputs, do that here,
        # before we feed the kwargs through to kivy's function.
        special_handling_dict = \
            self.handle_spec_inputs_for_init(kwargs)
        final_processed_vars = \
            self.spec_inputs_to_final_inputs(special_handling_dict,kwargs)

        # Formatted poorly for copy/pastability
        (
            no_repeated_classes    ,
            repeated_class_args    ,
            repeated_class_kwargs,
            extra_classes_args     ,
            extra_classes_kwargs   ,
        ) = (merge_recs(old_var,final_processed_vars[new_key])
                for old_var,new_key in zip(
                (
                    no_repeated_classes    ,
                    repeated_class_args    ,
                    repeated_class_kwargs  ,
                    extra_classes_args     ,
                    extra_classes_kwargs   ,
                ),
                self.desired_init_vars
                )
             )

        self.times_rpt_class = choose_new_or_old(
                            no_repeated_classes,self.no_repeated_classes)

        #process the arguments for the repeated class
        self.rpt_args =  repeated_class_args + self.repeated_class_args
        if repeated_class_kwargs:
            self.rpt_kwargs =  merge_dicts(self.repeated_class_kwargs,
                                           repeated_class_kwargs)
        else:
            self.rpt_kwargs =  self.repeated_class_kwargs

        #Process the arguments for the extra classes.
        if extra_classes_args:
            self.extra_args =  merge_dicts(self.extra_classes_args,
                                           extra_classes_args)
        else:
            self.extra_args =  self.extra_classes_args
        if extra_classes_kwargs:
            self.extra_kwargs =  merge_dicts(self.extra_classes_kwargs,
                                               extra_classes_kwargs)
        else:
            self.extra_kwargs =  self.extra_classes_kwargs




    def handle_spec_inputs_for_init(self,kwargs):
        '''
        If there is an argument that is unique to the class,
        process it as one of the existing argument
        :param kwargs:
        :return: defaultdict
        '''
        return_dict = defaultdict(lambda:None)
        for arg in list(kwargs.keys()):
            if arg in self.desired_kept_vars:
                return_dict[arg] = kwargs.pop(arg)

        return return_dict

    def _update_rect(self,instance,value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update_grid_size(self,new_no,new_args = None):
        '''

        :param new_no: The new number of children it needs
        :param new_args: dict or NoneType
        :return:
        '''
        #add information to allow for new arguments
        for repeat_widget in self.rpt_widgets:
            self.remove_widget(repeat_widget)
        self.rpt_widgets = []

        self.times_rpt_class = new_no
        self.add_repeated_class_widgets()


    def on_touch_up(self, touch):
        self.ready_for_update = False
        super(ChangeableBoxLayout,self).on_touch_up(touch)

    def spec_inputs_to_final_inputs(self,special_handling_dict,kwargs):
        '''
        Maps from the dictionary returned from the
        special_handle_inputs to the __init__ variables that our
        class uses, namely one of:

        no_repeated_classes
        repeated_class_args
        repeated_class_kwargs
        extra_classes_args
        extra_classes_kwargs

        :param special_handling_dict:
        :return: defaultdict
        '''
        return_dict = defaultdict(lambda:None)
        for field,value in special_handling_dict.items():
            return_dict[self.map_kept_attrs[field]] = value
        return return_dict

    def dispatch_update(self,*args,**kwargs):

        for child in self.rpt_widgets[:]:
            child.dispatch_update(*args,**kwargs)


class RecursiveBoxLayout(ChangeableBoxLayout):
    recursive_kw_args ={}
    def spec_inputs_to_final_inputs(self,special_handling_dict,kwargs):
        return_dict = super(RecursiveBoxLayout,self).\
            spec_inputs_to_final_inputs(special_handling_dict,kwargs)
        return_dict['repeated_class_kwargs'] = \
            {k:kwargs.pop(k)
             for k in self.recursive_kw_args}
        return return_dict


class SubBeat(ToggleButton):
    DEBUG=False

    def __init__(self,sound_file=None,*args,**kwargs):
        self.is_playing=False
        self.sound_file = 'audio/{}'.format(sound_file)
        self.sound = None
        super(SubBeat, self).__init__(*args,**kwargs)

    def play_sound(self,bar_x):
        if self.state=='down' and self.collide_point(bar_x,self.y):


            if not self.is_playing and self.sound:
                self.is_playing=True
                return self.sound.play()
        else:
            self.is_playing=False

    def on_press(self):
        if self.state=='down' and self.sound_file:
            self.sound = SoundLoader.load(self.sound_file)



class Beat(RecursiveBoxLayout):
    repeated_class = SubBeat
    no_repeated_classes = 1
    repeated_class_kwargs = {'orientation':'horizontal',
                             'spacing':10,
                             'pos_hint':{'y':.05},'size_hint':[1.,.9]
                             }

    #repeated_class_args = ()
    extra_classes = ()
    extra_classes_kwargs = defaultdict(tuple)
    extra_classes_args = defaultdict(dict)

    desired_kept_vars = ('no_subbeats',)
    map_kept_attrs = {'no_subbeats': 'no_repeated_classes'}
    recursive_kw_args = ('sound_file',)


    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                return self.prepare_touch_move(touch)

        super(ChangeableBoxLayout,self).on_touch_down(touch)

    def prepare_touch_move(self,touch):
        self.ready_for_update = True
        self.touch_coords =  touch.x,touch.y
        self.prev_grid = self.times_rpt_class

        for child in self.children[:]:
            #allow clicks to "undo" themselves (toggle buttons)
            if child.dispatch('on_touch_down', touch):
                return True
        else:
            return True

    def dispatch_update(self,*args,**kwargs):

        for subbeat in self.rpt_widgets[:]:
            subbeat.play_sound(bar_x=args[0])

    def on_touch_move(self, touch):
        if self.touch_coords and self.collide_point(*self.touch_coords):
            if self.ready_for_update:
                prev_x,prev_y = self.touch_coords
                graininess = self.height/3
                scaled_touch_diff = (touch.y-prev_y)-graininess/2
                if abs(scaled_touch_diff)>=graininess/2:
                    new_grid_size = int(self.prev_grid +
                                        (scaled_touch_diff//graininess))
                    new_grid_size = max(min(new_grid_size,6),1)
                    if new_grid_size!= self.times_rpt_class:
                        self.update_grid_size(new_grid_size)
                    return True

        super(ChangeableBoxLayout,self).on_touch_move(touch)


class Instrument(Beat):

    no_repeated_classes = 4

    repeated_class = Beat
    repeated_class_kwargs = {'orientation':'horizontal','spacing':10}

    #repeated_class_args = ()
    extra_classes = ()
    extra_classes_kwargs = defaultdict(tuple)
    extra_classes_args = defaultdict(dict)

    desired_kept_vars = ('no_beats',)#'no_subbeats')
    map_kept_attrs = {'no_beats': 'no_repeated_classes'}
    recursive_kw_args = ('no_subbeats','sound_file')
    def single_rpt_class(self):
        return self.repeated_class(
            bg_color = (random.random(),0.4,0.92),
            *self.rpt_args,**self.rpt_kwargs
        )

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.is_triple_tap:
                return self.prepare_touch_move(touch)

        super(ChangeableBoxLayout,self).on_touch_down(touch)

    def dispatch_update(self,*args,**kwargs):
        ChangeableBoxLayout.dispatch_update(self,*args,**kwargs)


class Measure(RecursiveBoxLayout):

    no_repeated_classes = 4

    repeated_class = Instrument
    repeated_class_kwargs = {'orientation':'horizontal','spacing':10}
    #repeated_class_args = ()
    extra_classes = ()
    extra_classes_kwargs = defaultdict(tuple)
    extra_classes_args = defaultdict(dict)

    desired_kept_vars = ('no_instruments',)#'no_beats','no_subbeats')
    map_kept_attrs = {'no_instruments': 'no_repeated_classes'}
    recursive_kw_args = ('no_beats','no_subbeats')

    def __init__(self,inst_sounds=None,**kwargs):

        if inst_sounds:
            self.inst_sounds = inst_sounds
        else:
            self.inst_sounds = []
        super(Measure,self).__init__(**kwargs)

    def add_repeated_class_widgets(self):
        for inst_sound in self.inst_sounds:
            inst = Instrument(sound_file=inst_sound,
                           *self.rpt_args,**self.rpt_kwargs)
            self.add_widget(inst)
            self.rpt_widgets.append(inst)



class RhythmMaker(FloatLayout):
    adj_const = 1.0/60.0 #60 seconds in a minute, tempo is in measures / min
    no_instruments = 4
    tempo = 30
    no_beats = 4
    no_subbeats = 1
    inst_list = ['hat3.mp3',
                 'tom3.mp3',
                 'snare3.mp3','kick3.mp3']
    def __init__(self):
        super(RhythmMaker,self).__init__()

        self.measure = Measure(
            inst_sounds=self.inst_list,
            no_instruments=self.no_instruments,
            no_beats = self.no_beats,
            no_subbeats = self.no_subbeats,
            orientation='vertical',
            spacing=5
        )

        self.add_widget(self.measure)

        self.progress_bar= prog_bar = CurrentProgressBar(
            pos = (0,0)
        )

        self.add_widget(
            prog_bar
        )


    def update(self,dt):
        dist_moved = dt*self.tempo*self.width*self.adj_const
        self.progress_bar.move(dist_moved)

        if self.progress_bar.x > self.width+10:
            self.progress_bar.x %= self.width+10

        self.measure.dispatch_update(self.progress_bar.x)


class Menu(Widget):
    pass


class CurrentProgressBar(Widget):
    def move(self,dist_moved):
        self.pos =  Vector(dist_moved,0.0) + self.pos


DEBUG_SOUND = True
class Sounds(object):

    def __init__(self):
        self.sounds = {}
        super(Sounds, self).__init__()

    def __getattr__(self, attr, volume=None):
        if not attr.startswith('play_'):
            return object.__getattribute__(self, attr)
        f = attr.split('play_')[1]
        sounds = getattr(self, 'sounds')
        loaded = sounds.get(f, [])
        ready = None
        for l in loaded:
            if l.state == 'stop':
                ready = l
                break
        if ready == None:
            ready = SoundLoader.load('audio/' + f + '.wav')
            sounds[f] = loaded
            loaded.append(ready)
        if DEBUG_SOUND:
            ready.play()
            while ready.state == 'play':
                pass
            return ready.play
        else:
            return lambda *args: None



class PolyRhythmApp(App):

    def build(self):
        self.root= root = RhythmMaker()
        Clock.schedule_interval(root.update, 1.0/120.0)
        return root

def choose_new_or_old(new,old):
    return new if new is not None else old

def merge_recs(old,new):
    if new is None:
        return old

    if isinstance(old, (tuple,list)):
        return old+new
    elif isinstance(old,dict):
        return_dict = old.copy()
        return_dict.update(new)
        return return_dict
    else:
        return new if new else old

if __name__ == '__main__':
    PolyRhythmApp().run()
