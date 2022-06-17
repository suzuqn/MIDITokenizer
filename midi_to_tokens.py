import pretty_midi

class midi_to_tokens():
    def __init__(self, path, steps_per_beat=12):
        self.steps_per_beat = steps_per_beat
        self.pm = pretty_midi.PrettyMIDI(path)
        
    def __call__(self):
        return ' '.join(self.tokens)
        
    def time_to_step(self, time):
        return round(self.pm.time_to_tick(time) / self.pm.resolution * self.steps_per_beat)
    
    def event_to_tokens(self, event):
        if event in ('bar', 'beat'):
            return [event]
        elif isinstance(event, pretty_midi.containers.Note):
            return [f'note_{event.pitch}', f'len_{self.time_to_step(event.end - event.start)}']
    
    @property
    def tokens(self):
        notes = []
        for inst in self.pm.instruments:
            notes += inst.notes
        notes.sort(key=lambda x: (x.start, -x.pitch))

        events = []
        events += [(self.time_to_step(db), 'bar') for db in self.pm.get_downbeats()]
        events += [(self.time_to_step(b), 'beat') for b in set(self.pm.get_beats()) - set(self.pm.get_downbeats())] # beats except for downbeats
        events += [(self.time_to_step(n.start), n) for n in notes]
        events.sort(key=lambda x: x[0])

        tokens = []
        last_beat = 0
        for step, event in events:
            if event in ('bar', 'beat'):
                last_beat = step
            if step - last_beat:
                tokens.append(f'pos_{step - last_beat}')
            tokens += self.event_to_tokens(event)

        return tokens