"""
development
~~~~~~~~~~~

Run a development server
"""


def main():
    from app import app
    app.debug = True
    app.run()
