"""
development
~~~~~~~~~~~

Run a development server
"""
from meg.app import create_app


app, _, _, celery = create_app(debug=True)


# kinda hacky. celery doesn't give me a choice
def main():
    app.run()
