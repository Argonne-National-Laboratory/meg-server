"""
development
~~~~~~~~~~~

Run a development server
"""
import argparse

from meg.app import create_app


# kinda hacky. celery doesn't give me a choice
app, _, _, celery = create_app(debug=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--all-interfaces", action="store_true")
    parser.add_argument("-p", "--port", default=5000, type=int, help="port to run on")
    args = parser.parse_args()
    if args.all_interfaces:
        app.run(host="0.0.0.0", port=args.port)
    else:
        app.run(port=args.port)
