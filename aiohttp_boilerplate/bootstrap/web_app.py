import importlib

from aiohttp import web


async def on_cleanup(app):
    # await app.db_pool.release(app.db)
    # await app.db_pool.terminate()
    await app.db_pool.close()


def start_web_app(conf, db_pool, loop=None):

    middlewares = []

    if conf.get('middlewares'):
        for middleware in conf['middlewares']:
            p, m = middleware.rsplit('.', 1)
            mod = importlib.import_module(p)
            met = getattr(mod, m)
            middlewares.append(met)

    # setup application and extensions
    app = web.Application(loop=loop, middlewares=middlewares)
    app.conf = conf
    app.db_pool = db_pool

    app.on_cleanup.append(on_cleanup)
    app.on_shutdown.append(on_cleanup)

    routes = importlib.import_module(conf['app_dir'] + '.routes')
    routes.setup_routes(app)
    return app
