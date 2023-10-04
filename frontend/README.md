# Linting and formatting
We use [biome](https://biomejs.dev/) for linting and formatting. During testing, `biome` will check whether all code conforms to the rules defined in `biome.json` - no PR's get through without conforming!

VS Code can be set up to autoformat on save through a [VS Code plugin](https://marketplace.visualstudio.com/items?itemName=biomejs.biome).

# Testing
We use [vitest](https://vitest.dev/) for testing. Tests can be run with

```
npm run test
```