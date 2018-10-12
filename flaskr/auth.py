import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
# 创建一个名称为'auth'的蓝图，认证蓝图，将包括注册新用户、登录或注销视图
bp = Blueprint('auth', __name__, url_prefix='/auth')


# 关联了URL/register和register视图函数。当Flask收到一个指向/auth/register的
# 请求时就会调用register视图并把其返回值作为响应
@bp.route('/register',methods=('GET','POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username=?',(username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)
        # fetchone()根据查询返回一个记录行。 如果查询没有结果，则返回
        # None 。后面还用到fetchall() ，它返回包括所有结果的列表。
        if error is None:
            db.execute(
                'Insert INTO user (username,password) VALUES(?,?)',
                (username,generate_password_hash(password))
                #  generate_password_hash() 生成安全的哈希值并储存到数据库中
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login',methods=('GET','POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        # 在数据库中查询并获取
        user = db.execute(
            'SELECT * FROM user WHERE username = ?',(username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'],password):
            error = 'Incorrect password.'
        # check_password_hash() 以相同的方式哈希提交的密码并安全的比较哈希值。如果匹配成功，那么密码就是正确的。

        # session是一个dict ，它用于储存横跨请求的值。
        # 当验证成功后，用户的id被储存于一个新的会话中。
        # 会话数据被储存到一个向浏览器发送的cookie中，在后继请求中，浏览器会返回它。
        # Flask会安全对数据进行签名以防数据被篡改。
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


'''
bp.before_app_request() 注册一个在视图函数之前运行的函数，
不论其 URL 是什么。 load_logged_in_user 检查用户 id 是否已经
储存在 session 中，并从数据库中获取用户数据，然后储存在 g.user 中。
g.user 的持续时间比请求要长。 如果没有用户 id ，或者 id 不存在，
那么 g.user 将会是 None 。
'''
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id=?',(user_id,)
        ).fetchone()


# 注销的时候需要把用户 id 从 session 中移除。
#  然后 load_logged_in_user 就不会在后继请求中载入用户了。
#  load_logged_in_user直接进入user_id is None分支
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# '''
# 装饰器返回一个新的视图，该视图包含了传递给装饰器的原视图。
# 新的函数检查用户 是否已载入。如果已载入，那么就继续正常执行原视图，
# 否则就重定向到登录页面。 我们会在博客视图中使用这个装饰器。
# '''
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return wrapped_view
