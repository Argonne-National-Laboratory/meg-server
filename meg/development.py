"""
development
~~~~~~~~~~~

Run a development server
"""
from meg.app import create_app


def main():
    app, _ = create_app(debug=True)
    app.run()
