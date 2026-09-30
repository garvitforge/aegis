"""Optional image output (GIF replays and charts). Requires Pillow: pip install "aegis-robotics[viz]"."""

from .grid import GridMap, Position
from .exploration import frontier_cells
from .mapping import OccupancyMap
from .trace import reachable_free_count, replay_states

UNKNOWN = (27, 31, 39)
FREE = (232, 236, 241)
OBSTACLE = (43, 58, 85)
FRONTIER = (245, 165, 36)
TRAIL = (156, 201, 255)
ROBOT = (255, 77, 79)
BASE = (46, 204, 113)
TEXT = (232, 236, 241)
GRID_LINE = (20, 23, 30)


def _pil():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:  # pragma: no cover - exercised only without Pillow
        raise RuntimeError('Pillow is required for image output: pip install "aegis-robotics[viz]"') from exc
    return Image, ImageDraw, ImageFont


def render_frame(
    known: OccupancyMap,
    robot: Position,
    trail: list[Position],
    base: Position,
    label: str,
    cell: int = 22,
):
    Image, ImageDraw, ImageFont = _pil()
    header = 28
    width, height = known.width * cell, known.height * cell
    image = Image.new("RGB", (width, height + header), UNKNOWN)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    frontiers = frontier_cells(known.known_free, known.known_obstacles, known.width, known.height)
    trail_set = set(trail)

    for x in range(known.width):
        for y in range(known.height):
            pos = (x, y)
            if pos in known.known_obstacles:
                color = OBSTACLE
            elif pos in known.known_free:
                color = TRAIL if pos in trail_set else FREE
            elif pos in frontiers:
                color = FRONTIER
            else:
                color = UNKNOWN
            x0, y0 = x * cell, header + y * cell
            draw.rectangle([x0, y0, x0 + cell - 2, y0 + cell - 2], fill=color)

    bx, by = base
    draw.rectangle(
        [bx * cell + 4, header + by * cell + 4, bx * cell + cell - 6, header + by * cell + cell - 6],
        outline=BASE,
        width=2,
    )
    rx, ry = robot
    draw.ellipse(
        [rx * cell + 3, header + ry * cell + 3, rx * cell + cell - 5, header + ry * cell + cell - 5],
        fill=ROBOT,
    )
    draw.text((6, 8), label, fill=TEXT, font=font)
    return image


def save_replay_gif(
    truth: GridMap,
    start: Position,
    positions: list[Position],
    sensor_range: int,
    path: str,
    cell: int = 22,
    frame_ms: int = 70,
    max_frames: int = 220,
) -> int:
    """Write an animated GIF of a mission. Returns the number of frames written."""
    states = list(replay_states(truth, start, positions, sensor_range))
    total = reachable_free_count(truth, start)

    indices = list(range(len(states)))
    if len(indices) > max_frames:
        stride = len(indices) / max_frames
        indices = sorted({int(i * stride) for i in range(max_frames)} | {len(states) - 1})

    frames = []
    for i in indices:
        pos, known = states[i]
        trail = [p for p, _ in states[: i + 1]]
        coverage = len(known.known_free) / total * 100
        label = f"AEGIS-Sim   move {i}/{len(states) - 1}   coverage {coverage:5.1f}%"
        frames.append(render_frame(known, pos, trail, start, label, cell))

    durations = [frame_ms] * len(frames)
    durations[-1] = 1500
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    return len(frames)


def save_coverage_chart(curves: dict[str, list[float]], path: str, title: str = "Map coverage vs. moves") -> None:
    """Draw mean coverage curves as a simple line chart PNG."""
    Image, ImageDraw, ImageFont = _pil()
    w, h = 720, 420
    left, right, top, bottom = 60, 20, 40, 50
    image = Image.new("RGB", (w, h), (16, 19, 26))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    palette = {"random_walk": (150, 150, 160), "nearest": (90, 170, 255), "scored": (245, 165, 36)}

    length = max(len(v) for v in curves.values()) - 1
    plot_w, plot_h = w - left - right, h - top - bottom

    def px(step: int, value: float) -> tuple[int, int]:
        return left + int(step / length * plot_w), top + int((1 - value) * plot_h)

    for tick in (0.0, 0.25, 0.5, 0.75, 1.0):
        _, y = px(0, tick)
        draw.line([(left, y), (w - right, y)], fill=(40, 46, 58))
        draw.text((14, y - 5), f"{int(tick * 100)}%", fill=TEXT, font=font)
    for step in range(0, length + 1, max(1, length // 6)):
        x, _ = px(step, 0)
        draw.text((x - 8, h - bottom + 8), str(step), fill=TEXT, font=font)
    draw.text((left, 14), title, fill=TEXT, font=font)
    draw.text((w // 2 - 20, h - 22), "moves", fill=TEXT, font=font)

    legend_x = w - right - 150
    for n, (name, values) in enumerate(curves.items()):
        color = palette.get(name, (255, 255, 255))
        points = [px(i, v) for i, v in enumerate(values)]
        draw.line(points, fill=color, width=3)
        ly = top + 6 + n * 16
        draw.line([(legend_x, ly + 4), (legend_x + 18, ly + 4)], fill=color, width=3)
        draw.text((legend_x + 24, ly), name, fill=TEXT, font=font)

    image.save(path)
