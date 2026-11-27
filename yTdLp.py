import asyncio
import os
import subprocess
import tempfile

import yt_dlp

import FFMpe
import TrANs


class DownloadError(Exception):
    pass


class ProcessError(Exception):
    pass


def _download(url: str, output_dir: str, mode: str) -> str:
    opts = {
        "format": "bv*+ba/b",
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded = ydl.prepare_filename(info)
            ext = downloaded.rsplit(".", 1)[1]
            file_id = TrANs.id_feli("download", mode, url, ext)
            target = os.path.join(output_dir, f"{file_id}.{ext}")
            os.replace(downloaded, target)
            return target
    except Exception as exc:
        raise DownloadError from exc


def _download_audio(url: str, output_dir: str, mode: str) -> str:
    opts = {
        "format": "ba/b",
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded = ydl.prepare_filename(info)
            ext = downloaded.rsplit(".", 1)[1]
            file_id = TrANs.id_feli("download", mode, url, ext)
            target = os.path.join(output_dir, f"{file_id}.{ext}")
            os.replace(downloaded, target)
            return target
    except Exception as exc:
        raise DownloadError from exc


async def _run_ffmpeg(func, *args) -> None:
    try:
        await asyncio.to_thread(func, *args)
    except subprocess.CalledProcessError as exc:
        raise ProcessError from exc


async def process_animation(
    url: str, target_dir: str, rotation: str, mirror: bool, triple: bool,
) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        downloaded = await asyncio.to_thread(_download, url, tmp, "sticker")
        file_id = TrANs.id_feli("sticker", url, "mp4", rotation, mirror, triple)
        output = os.path.join(target_dir, f"{file_id}.mp4")
        await _run_ffmpeg(
            FFMpe.to_animation, downloaded, output, rotation, mirror, triple
        )
        return output


async def process_video_note(
    url: str, target_dir: str, rotation: str, mirror: bool, triple: bool,
) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        downloaded = await asyncio.to_thread(_download, url, tmp, "videonote")
        file_id = TrANs.id_feli("videonote", url, "mp4", rotation, mirror, triple)
        output = os.path.join(target_dir, f"{file_id}.mp4")
        await _run_ffmpeg(
            FFMpe.to_video_note, downloaded, output, rotation, mirror, triple
        )
        return output


async def process_voice(url: str, target_dir: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        downloaded = await asyncio.to_thread(_download_audio, url, tmp, "voice")
        file_id = TrANs.id_feli("voice", url, "ogg")
        output = os.path.join(target_dir, f"{file_id}.ogg")
        await _run_ffmpeg(FFMpe.to_voice, downloaded, output)
        return output


async def process_default(url: str, target_dir: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        downloaded = await asyncio.to_thread(_download, url, tmp, "default")
        ext = os.path.basename(downloaded).rsplit(".", 1)[1]
        file_id = TrANs.id_feli("default", url, ext)
        target = os.path.join(target_dir, f"{file_id}.{ext}")
        os.replace(downloaded, target)
        return target
