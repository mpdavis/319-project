import sys, os
ROOT_PATH = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
LIB_PATH = os.path.join(ROOT_PATH, 'lib')
sys.path.insert(0, LIB_PATH)
sys.path.insert(0, ROOT_PATH)

from flask import Flask
from flask_assets import Environment, Bundle, ManageAssets
from flask.ext.script import Manager

app = Flask('main')
app.config.from_object('settings')

assets_env = Environment(app)
js = Bundle(Bundle('js/jquery-1.7.1.min.js'), Bundle('js/bootstrap.min.js'),
            Bundle('js/chosen.jquery.min.js', 'js/chosen.autoload.js'),
            Bundle('js/bootstrap-modal.js'), Bundle('js/jquery.datatable.js'),
            Bundle('js/boostrap-datepicker.js'), Bundle('js/jquery-ui.min.js'),
            output='merged/merged.js')
assets_env.register('js_all', js)

css = Bundle('css/bootstrap.css', 'css/chosen.css', 'css/styles.css', 'css/datepicker.css',
             filters='cssmin', output='merged/merged.css')
assets_env.register('css_all', css)
#comment out later?
assets_env.add(js)
js.build()

assets_env.add(css)
css.build()

manager = Manager(app)
manager.add_command("assets", ManageAssets(assets_env))

if __name__ == "__main__":
    manager.run()
