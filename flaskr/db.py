import sqlite3


import click
from flask import current_app,g
# g是一个特殊的对象，独立于每一个请求。
# 在处理请求过程中，它可以用于储存可能多个函数都会用到的数据。把连接储存于其中，可以多次使用

# current_app对象指向处理请求的Flask应用。
# 这里使用了应用工厂，那么在其余的代码中就不会出现应用对象。
# 当应用创建后，在处理一个请求时，get_db会被调用。这样就需要使用current_app
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        # 新建连接
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # 告诉连接返回类似于字典的行，这样可以通过列名称来操作数据。
        # 即数据可以按表中的每一行返回
    return g.db


def close_db(e=None):
    '''
    close_db 通过检查 g.db 来确定连接是否已经建立。
    如果连接已建立，那么 就关闭连接。
    以后会在应用工厂中告诉应用 close_db 函数，这样每次请求后就会 调用它。
    :param e:
    :return:
    '''
    db = g.pop('db',None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()  # get_db()返回一个数据库连接

    # open_resource() 打开一个文件，该文件名是相对于 flaskr 包的
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))


# 定义一个名为 init-db 命令行,它调用 init_db 函数，并为用户显示一个成功的消息
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo('Initialized the database')


def init_app(app):
    app.teardown_appcontext(close_db)  # 告诉Flask在返回响应后进行清理的时候调用此函数(close_db)
    app.cli.add_command(init_db_command)  # 添加一个新的可以与flask一起工作的命令

