import copy
import pretty_midi

class midi_to_tokens():
    def __init__(self, path, steps_per_beat=12):
        self.steps_per_beat = steps_per_beat
        self.pm = pretty_midi.PrettyMIDI(path)
        self.dbs = self.pm.get_downbeats().tolist() + [self.pm.get_end_time()] # dbs := downbeats
        self.tokens = self._tokenize()
        
    def __call__(self):
        return ' '.join(self.tokens)
        
    def _time_to_step(self, time):
        return round(self.pm.time_to_tick(time) / self.pm.resolution * self.steps_per_beat)
    
    def _event_to_tokens(self, event):
        if event in ('bar', 'beat'):
            return [event]
        elif isinstance(event, pretty_midi.containers.Note):
            return [f'note_{event.pitch}', f'len_{self._time_to_step(event.end - event.start)}']
        
    def _trim_note(self, note, start, end):
        n = copy.copy(note)
        n.start, n.end = max(n.start, start), min(n.end, end)
        return n
    
    def _tokenize(self, start_measure=1, end_measure=None):
        start, end = self.dbs[start_measure - 1], self.dbs[end_measure or -1]
        
        notes = []
        for inst in self.pm.instruments:
            notes += inst.notes
        notes.sort(key=lambda x: (x.start, -x.pitch))

        events = []
        events += [(self._time_to_step(db), 'bar') for db in self.dbs if start <= db < end]
        events += [(self._time_to_step(b), 'beat') for b in set(self.pm.get_beats()) - set(self.dbs) if start <= b < end] # beats without downbeats
        events += [(self._time_to_step(max(n.start, start)), self._trim_note(n, start, end)) for n in notes if start <= n.start < end or start < n.end <= end]        
        events.sort(key=lambda x: x[0])
        
        tokens = []
        last_beat = 0
        for step, event in events:
            if event in ('bar', 'beat'):
                last_beat = step
            if step - last_beat:
                tokens.append(f'pos_{step - last_beat}')
            tokens += self._event_to_tokens(event)

        return tokens
    
    def measures(self, start_measure=1, end_measure=None):
        return self._tokenize(start_measure, end_measure)