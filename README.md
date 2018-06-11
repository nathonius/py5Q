# py5Q: Python bindings for the Das Keyboard 5Q
## Installation
For now, you'll need to clone the repo and import the repo in another script.

## Usage

```python
import py5Q
Q = py5Q.py5Q(clientId='YOUR ID', clientSecret='YOUR SECRET')

# Make the A key red
signalId = Q.signal('KEY_A', '#ff0000')

# Delete a signal
Q.delete(signalId)

# Batch signals
signalIds = Q.batchSignal(('KEY_A', 'KEY_S', '2,2'), '#00ff00')

# Batch signal range
# Make the entire 'Insert' through 'Page Down' section of the keyboard blue
rangeIds = Q.batchSignalRange((16, 18), (1, 2), '#0000ff')

# Special zones
# Make numpad yellow
numpadSignals = Q.batchSignal(Q.zones.numpad, '#ffff00')

# Delete ALL signals
Q.deleteAll()
```

## Automatic Authentication
If no `clientId` and `clientSecret` are specified, they will be loaded from a file called `config.json` in the same folder as the `py5Q.py` file. The file is formatted like this:

```json
{
    "clientId": "YOUR ID",
    "clientSecret": "YOUR SECRET",
    "username": "",
    "password": ""
}
```

With that file, the object can be created like this:

```python
import py5Q
Q = py5Q.py5Q()
```
