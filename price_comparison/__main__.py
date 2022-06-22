import uvloop

from price_comparison.runner import run_api

if __name__ == '__main__':
    uvloop.install()
    run_api()
