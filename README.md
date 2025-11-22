# werewolf-agent

Platform for the 1st Agent Development Competition, themed around the game Werewolf.

## Usage

This platform consists of several components:

- Unity Client (`client`)
- Python SDK (`sdk`)
- Game Server (`server`)

Checkout `README.md` in corresponding directories for usage of different components.

## Contributing

PRs accepted!

For developers, some key points to be followed, especially for ASTA members:
- Make sure your code can pass CI checks, including pylint and black.
- Comment your code appropriately. For documentation comments in Python, you can refer [this repository](https://github.com/thuasta/saiblo-worker).
- Don't contain any non-ascii character in your source code, including Chinese, especially in comments and logging messages. If you are using AI-assisted coding, remember to remind it to comment in English.
- Follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/). [This VSCode plugin](https://marketplace.visualstudio.com/items?itemName=vivaxy.vscode-conventional-commits) may help.

## License

- Platform: GPL-3.0-only © ASTA
- SDK: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication