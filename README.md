Basic usage is like this:

    import py5Q
    q = py5Q.pyQ(clientId='YOUR ID', secret='YOUR SECRET')
    id = q.signal("KEY_A", "#ff0000")
    # ... do some stuff ... #
    q.delete(id)

Also has built in batch signals. You can either do a list of zones (`batchSignal`) or do a range of coordinates (`batchSignalRange`).

While `batchSignal` is self explanatory, `batchSignalRange` works like this:

    # set tilde throuh = key to be red
    # batchSignalRange((x1, x2), (y1, y2), ...params)
    signals = q.batchSignalRange((1, 13), (1, 1), "#ff0000")

The main thing this provides is an authentication handler that automatically gets a new token when needed. Everything else is sugar. I'll keep working on it in my spare time; there's still plenty to do.
