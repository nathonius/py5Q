import py5Q
Q = py5Q.py5Q()

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

Q.deleteAll()
