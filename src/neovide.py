#!/usr/bin/env python3
# https://github.com/gmanka-flatpaks/flatpak-gen

__license__ = "LGPL-3.0"


import asyncio
from generators import pip, cargo


async def main():
    packages = [
        cargo(
            write_path='neovide-cargo-sources.yml',
            cargo_lock_url='https://raw.githubusercontent.com/neovide/neovide/9c23c432b8105f39d9e9ddc2732d3350a0323cc9/Cargo.lock',
        ),
        cargo(
            write_path='ripgrep-cargo-sources.yml',
            cargo_lock_url='https://raw.githubusercontent.com/BurntSushi/ripgrep/4649aa9700619f94cf9c66876e9549d83420e16c/Cargo.lock',
        ),
        pip(
            write_path='python3-pynvim',
            package='pynvim',
        ),
    ]
    for package in packages:
        await package.generate()


asyncio.run(main())

