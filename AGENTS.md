# Development

Keep changes small and send them as pull requests. CI runs the test suite on
Python 3.11 to 3.13, and Greptile reviews each pull request.

Run `python -m unittest discover -s tests -v` before pushing code changes.

## Benchmarks

Keep each benchmark in its own `benchmarks/<test>/rounds/<round>/` directory.
Never rewrite archived results. Distinguish inferred links from observed
execution. Never claim a provider score is a calibrated probability or that a
missing link proves a test is irrelevant. Preserve ordinary search and test
fallbacks.

## Secrets

Never ask for secrets in chat or commit them. Provide `TYPESAFE_API_KEY`
through the environment or a private env file passed with `--env-file`. With
[tokenstash](https://github.com/krishhgg/tokenstash), run
`tokenstash need TYPESAFE_API_KEY`. Exit 0 means the key is in the env file,
10 means it's pending, and 20 means it was denied, so use a non-secret
fallback. Never commit env files or local `.jev-map/` maps.
