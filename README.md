# py5Q: Python bindings for the Das Keyboard 5Q
## Installation
For now, you'll need to clone the repo.

## Script Usage

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

## Command Line Usage
For now, CLI usage *requires* automatic authentication.

```
// A Key -> Red
py5Q.py signal -z KEY_A -c #ff0000

// Delete all signals
py5Q.py delete --all
```

#### Full Command Line Reference
#### Global Options
option (short)|effect|default|example
---|---|---|---
signal|Send a signal.|None. `signal` or `delete` is required.|`signal`
delete|Delete a signal.|None. `signal` or `delete` is required|`delete`
--no-cache|Do not used cached tokens. Forces re-authentication.|None|`--no-cache`

#### signal Options

option (short)|effect|default|example
------|------|-------|-------
--zones (-z)|Which zones to affect. Can be one or a list.|No default. This option is required.|`--zones KEY_A KEY_B`
--color (-c)|Color to set.|No default. This option is required.|`--color #ff0000`
--name (-n)|Name of signal.|`"py5Q Signal"`|`--name "My Signal"`
--effect (-e)|Effect to use. See [here](https://www.daskeyboard.io/q-api-doc/#effects) for a list.|`SET_COLOR`|`--effect BLINK`
--message (-m)|Signal message.|None|`--message "Signal message."`
--notify|Sets `shouldNotify` true.|None|`--notify`
--read (-r)|Sets `isRead` true.|None|`--read`
--archived (-a)|Sets `isArchived` true.|None|`--archived`
--muted|Sets `isMuted` true.|None|`--muted`

#### delete Options

option (short)|effect|default|example
--------------|------|-------|------
--all (-a)|Ignores any given IDs and instead deletes ALL signals.|None|`--all`
signals|A list of signal IDs to delete|None|`delete <ID1> <ID2> <ID3> ...`

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

## Token Caching
Unless `--no-cache` is specified on the CLI or the py5Q object is created with `cacheTokens=False`, tokens will be read from a `tokens.json` file in the same directory as the script.
