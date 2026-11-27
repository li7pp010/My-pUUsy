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


def _download(url: str, output_dir: str) -> str:
    opts = {
        "format": "bv*+ba/b",
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded = ydl.prepare_filename(info)
            name = TrANs.build_name(info)
            ext = downloaded.rsplit(".", 1)[1]
            target = os.path.join(output_dir, f"{name}.{ext}")
            os.replace(downloaded, target)
            return target
    except Exception as exc:
        raise DownloadError from exc


def _download_audio(url: str, output_dir: str) -> str:
    opts = {
        "format": "ba/b",
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded = ydl.prepare_filename(info)
            name = TrANs.build_name(info)
            ext = downloaded.rsplit(".", 1)[1]
            target = os.path.join(output_dir, f"{name}.{ext}")
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
    url: str, chat_id: int, user_id: int, is_private: bool,
    rotation: str, mirror: bool, triple: bool,
) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        target_dir = TrANs.build_dir(chat_id, user_id, is_private)
        downloaded = await asyncio.to_thread(_download, url, tmp)
        base = os.path.splitext(os.path.basename(downloaded))[0]
        output = os.path.join(target_dir, f"{base}.mp4")
        await _run_ffmpeg(
            FFMpe.to_animation, downloaded, output, rotation, mirror, triple
        )
        return output


async def process_video_note(
    url: str, chat_id: int, user_id: int, is_private: bool,
    rotation: str, mirror: bool, triple: bool,
) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        target_dir = TrANs.build_dir(chat_id, user_id, is_private)
        downloaded = await asyncio.to_thread(_download, url, tmp)
        base = os.path.splitext(os.path.basename(downloaded))[0]
        output = os.path.join(target_dir, f"{base}.mp4")
        await _run_ffmpeg(
            FFMpe.to_video_note, downloaded, output, rotation, mirror, triple
        )
        return output


async def process_voice(
    url: str, chat_id: int, user_id: int, is_private: bool
) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        target_dir = TrANs.build_dir(chat_id, user_id, is_private)
        downloaded = await asyncio.to_thread(_download_audio, url, tmp)
        base = os.path.splitext(os.path.basename(downloaded))[0]
        output = os.path.join(target_dir, f"{base}.ogg")
        await _run_ffmpeg(FFMpe.to_voice, downloaded, output)
        return output


async def process_default(
    url: str, chat_id: int, user_id: int, is_private: bool
) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        target_dir = TrANs.build_dir(chat_id, user_id, is_private)
        downloaded = await asyncio.to_thread(_download, url, tmp)
        base = os.path.basename(downloaded)
        target = os.path.join(target_dir, base)
        os.replace(downloaded, target)
        return target
