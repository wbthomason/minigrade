minigrade
=========

A lightweight automatic grading system for CS courses.
Usage:
The main grading workflow happens in grade_stream in minigrade.py. It's a generator, and so (should) stream results back to the user as they come in. To run the server for debugging, run "python minigrade.py" with Python 2.x. It will bind to 9080 by default. If you change the port, or are trying to run it on a different server, you'll need to update the relevant information in the "audience" portion of login().
To actually run the server for use, run "python tornados.py", again with Python 2.x.
