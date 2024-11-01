#!/usr/bin/env python3
# https://github.com/gmanka-flatpaks/flatpak-gen

__license__ = "LGPL-3.0"

from pathlib import Path
import flatpak_cargo_generator.script
import tomllib
import asyncio
import aiohttp
import yaml
import sys


class path:
    file = Path(__file__)
    repo = Path(__file__).parent.parent.resolve()
    ouptut = repo / 'output'
    generators_src = file.parent.resolve()


class pip:
    def __init__(
        self,
        write_path: str,
        package: str,
        use_output_dir: bool = True,
    ) -> None:
        if use_output_dir:
            self.write_path: Path = get_output_path(write_path)
        else:
            self.write_path: Path = Path(write_path)
        self.package: str = package

    async def generate(self):
        print()
        commands = [
            sys.executable,
            '-m',
            'flatpak_pip_generator',
            '--yaml',
            '--checker-data',
            f'--output={self.write_path}',
            self.package,
        ]
        proc = await asyncio.create_subprocess_exec(
            *commands
        )
        await proc.wait()


def get_output_path(
    filename,
) -> Path:
    path.ouptut.mkdir(
        exist_ok=True,
        parents=True,
    )
    return path.ouptut / filename


class cargo:
    def __init__(
        self,
        write_path: str,
        cargo_lock_file: str = '',
        cargo_lock_url: str = '',
        use_output_dir: bool = True,
    ) -> None:
        if use_output_dir:
            self.write_path: Path = get_output_path(write_path)
        else:
            self.write_path: Path = Path(write_path)
        self.cargo_lock_url: str = cargo_lock_url
        self.cargo_lock_file: str = cargo_lock_file

    async def download(
        self,
        url: str,
    ) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    async def generate(self):
        if self.cargo_lock_file and self.cargo_lock_url:
            raise ValueError('cargo_lock_file and cargo_lock_url should not used both')
        elif self.cargo_lock_url:
            cargo_lock_data: str = await self.download(
                self.cargo_lock_url
            )
        elif self.cargo_lock_file:
            cargo_lock_data: str = Path(self.cargo_lock_file).read_text()
        else:
            raise ValueError('please set cargo_lock_file or cargo_lock_url')
        lock_dict: dict = tomllib.loads(cargo_lock_data)
        data = await flatpak_cargo_generator.script.generate_sources(
                cargo_lock=lock_dict,
        )
        with open(self.write_path, 'w') as fp:
            fp.write(
                '# generated with flatpak-cargo-gen & https://github.com/gmanka-flatpaks/flatpak-gen\n'
            )
            yaml.dump(data, fp)

