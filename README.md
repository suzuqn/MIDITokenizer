# MIDI Tokenizer

A simple MIDI Tokenizer in the style of [Score Transformer](https://github.com/suzuqn/ScoreTransformer)

## Usage

```python
from midi_to_tokens import midi_to_tokens

tokens = midi_to_tokens('path/to/midi', steps_per_beat=12).tokens
```

## Supported tokens
- **bar** : measure/downbeat
- **beat** : beat
- **pos** : position
- **note** : note pitch
- **len** : note length/duration
