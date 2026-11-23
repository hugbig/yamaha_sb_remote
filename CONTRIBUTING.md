# Contributing

Thanks for your interest. Bug reports, results from other soundbar models and pull requests are
welcome.

## Reporting a bug

Open an [issue](../../issues/new/choose) with the soundbar model, the Home Assistant version, the
integration version, the Bluetooth adapter you use (local or ESPHome proxy) and the integration
debug logs. Results from soundbars other than the SR-C20A are especially useful.

## Making a change

1. Open an issue first for anything larger than a small fix, so we can agree on the approach.
2. Create a branch from `main`.
3. Add or update tests for any behaviour you change, and run the lint and the tests:

   ```sh
   pip install -r requirements-test.txt
   ruff check .
   pytest
   ```

4. If possible, check the change on a real soundbar and say so in the pull request.
5. Write commit messages in the [Conventional Commits](https://www.conventionalcommits.org) style
   (`feat:`, `fix:`, `docs:`, `test:`…) and add a line to [CHANGELOG.md](CHANGELOG.md) for
   user-visible changes.

## License

By contributing, you agree that your contributions are released under the [MIT license](LICENSE).
