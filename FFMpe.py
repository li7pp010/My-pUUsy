import subprocess


def _rotation_filter(rotation: str, triple: bool) -> str | None:
    if rotation == "right":
        return "transpose=1" if not triple else "transpose=1,transpose=1,transpose=1"
    if rotation == "left":
        return "transpose=2" if not triple else "transpose=2,transpose=2,transpose=2"
    return None


def to_animation(
    input_path: str, output_path: str, rotation: str, mirror: bool, triple: bool
) -> None:
    filters = []
    rotation_filter = _rotation_filter(rotation, triple)
    if rotation_filter:
        filters.append(rotation_filter)
    if mirror:
        filters.append("hflip")
    filters.append("scale=trunc(iw/2)*2:trunc(ih/2)*2")
    cmd = ["ffmpeg", "-y", "-i", input_path, "-an", "-c:v", "libx264"]
    cmd += ["-vf", ",".join(filters)]
    cmd += ["-f", "mp4", output_path]
    subprocess.run(cmd, check=True, capture_output=True)


def to_video_note(
    input_path: str, output_path: str, rotation: str, mirror: bool, triple: bool
) -> None:
    filters = []
    rotation_filter = _rotation_filter(rotation, triple)
    if rotation_filter:
        filters.append(rotation_filter)
    if mirror:
        filters.append("hflip")
    filters += ["crop=ih:ih", "scale=640:640", "setsar=1"]
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", input_path,
            "-t", "60",
            "-vf", ",".join(filters),
            "-c:v", "libx264",
            "-f", "mp4",
            output_path,
        ],
        check=True,
        capture_output=True,
    )


def to_voice(input_path: str, output_path: str) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", input_path,
            "-vn", "-c:a", "libopus",
            "-f", "ogg",
            output_path,
        ],
        check=True,
        capture_output=True,
    )


def cut_media(input_path: str, output_path: str, start: float, end: float) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", input_path,
            "-ss", str(start), "-to", str(end),
            "-c", "copy",
            output_path,
        ],
        check=True,
        capture_output=True,
    )
