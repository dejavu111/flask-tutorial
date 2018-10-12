import os

from flask import Flask


# 应用工厂函数
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__,instance_relative_config=True)  # 创建Flask实例
    # __name__表示当前Python模块的名称
    # instance_relative_config=True告诉应用配置文件是相对于instance folder 的相对路径。
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path,'flaskr.sqlite'),  # 数据库文件存放的路径
    )

    if test_config is None:
        # load the instance config,if it exists,when not testing
        app.config.from_pyfile('config.py',silent=True)  # 使用config.py中的值来重载缺省配置
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello,World'

    from . import db
    db.init_app(app)

    # app.register_blueprint()在工厂中导入和注册蓝图
    from . import auth
    app.register_blueprint(auth.bp)

    # 与验证蓝图不同，博客蓝图没有 url_prefix 。
    # 因此 index 视图会用于 / ， create 会用于 /create ，以此类推。
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/',endpoint='index')

    return app

