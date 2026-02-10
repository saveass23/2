from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class DotaBranchLot:
    branch: str
    emoji: str
    title: str
    offer_points: tuple[str, ...]
    cta: str

    def render_description(self) -> str:
        points = "\n".join(f"• {point}" for point in self.offer_points)
        return (
            f"{self.emoji} <b>{self.title}</b>\n"
            f"🎯 Ветка: <b>{self.branch}</b>\n"
            f"{points}\n"
            f"\n✅ Гарантия: безопасно, быстро, без передачи аккаунта\n"
            f"📩 {self.cta}"
        )


DEFAULT_LOTS: tuple[DotaBranchLot, ...] = (
    DotaBranchLot(
        branch="Поднятие MMR",
        emoji="🏆",
        title="Dota 2 — Быстрый буст рейтинга",
        offer_points=(
            "От 1 до 1000+ MMR по вашему заказу",
            "Играем аккуратно, с высоким винрейтом",
            "Ежедневный отчёт по прогрессу",
        ),
        cta="Напишите желаемый MMR и текущий рейтинг — стартуем сразу!",
    ),
    DotaBranchLot(
        branch="Калибровка",
        emoji="📊",
        title="Dota 2 — Калибровка аккаунта под ключ",
        offer_points=(
            "Поможем выйти на максимум по калибровочным играм",
            "Индивидуальная стратегия под ваш пул героев",
            "Советы по закреплению результата",
        ),
        cta="Отправьте текущий скрытый рейтинг и желаемый результат.",
    ),
    DotaBranchLot(
        branch="Порядочность",
        emoji="🛡️",
        title="Dota 2 — Поднятие порядочности",
        offer_points=(
            "Поднимем Behaviour Score и Communication Score",
            "Мягкий режим без токсичности и репортов",
            "Работаем до согласованного результата",
        ),
        cta="Напишите текущую порядочность — рассчитаем сроки и цену.",
    ),
    DotaBranchLot(
        branch="Ролевой рейтинг",
        emoji="🎮",
        title="Dota 2 — Ролевой буст (Core/Support)",
        offer_points=(
            "Поднимаем рейтинг на нужной роли",
            "Гибкий выбор позиции: 1/2/3/4/5",
            "Сохраняем стиль игры и статистику",
        ),
        cta="Укажите роль и диапазон MMR для буста.",
    ),
    DotaBranchLot(
        branch="Обучение",
        emoji="🧠",
        title="Dota 2 — Персональный коучинг",
        offer_points=(
            "Разбор реплеев и ошибок по таймингам",
            "План роста по микро и макро-игре",
            "Практика в пати + домашние задания",
        ),
        cta="Пришлите ваш Dotabuff/ID матча — подготовим план прокачки.",
    ),
)


def build_lot_rows(lots: Iterable[DotaBranchLot]) -> list[dict[str, str]]:
    return [
        {
            "branch": lot.branch,
            "title": lot.title,
            "description_html": lot.render_description(),
        }
        for lot in lots
    ]


def export_to_csv(rows: list[dict[str, str]], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["branch", "title", "description_html"])
        writer.writeheader()
        writer.writerows(rows)


def export_to_text(rows: list[dict[str, str]], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    blocks = []
    for index, row in enumerate(rows, start=1):
        blocks.append(
            "\n".join(
                (
                    f"Лот #{index}",
                    f"Ветка: {row['branch']}",
                    f"Заголовок: {row['title']}",
                    "Описание:",
                    row["description_html"],
                )
            )
        )
    destination.write_text("\n\n".join(blocks), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Генератор красивых лотов для FunPay по Dota 2: "
            "создаёт по одному лоту на каждую ветку."
        )
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("output/funpay_dota_lots.csv"),
        help="Путь для CSV-файла (по умолчанию: output/funpay_dota_lots.csv)",
    )
    parser.add_argument(
        "--txt",
        type=Path,
        default=Path("output/funpay_dota_lots.txt"),
        help="Путь для TXT-файла (по умолчанию: output/funpay_dota_lots.txt)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_lot_rows(DEFAULT_LOTS)
    export_to_csv(rows, args.csv)
    export_to_text(rows, args.txt)
    print(f"Готово! Создано {len(rows)} лотов.")
    print(f"CSV: {args.csv}")
    print(f"TXT: {args.txt}")


if __name__ == "__main__":
    main()
