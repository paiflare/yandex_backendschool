from aiohttp import web

from price_comparison.api.app import create_app


def run_api() -> None:
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=80)
