# /usr/bin/env bash
set -e

pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}


pushd cache_transactions && pwd
pushd python && uv pip install --upgrade moneykit && popd
popd

pushd create_link/backend && pwd
pushd python && uv pip install --upgrade moneykit && popd
pushd ruby && bundle update moneykit && popd
popd


pushd fetch_products && pwd
pushd python && uv pip install --upgrade moneykit && popd
pushd ruby && bundle update moneykit && popd
popd

pushd use_webhooks/backend && pwd
pushd python && uv pip install --upgrade moneykit && popd
pushd ruby && bundle update moneykit && popd
popd
