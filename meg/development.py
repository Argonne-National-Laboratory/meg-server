"""
development
~~~~~~~~~~~

Run a development server
"""
from meg.app import create_app


def main():
    app = create_app(debug=True)
    app.run()
