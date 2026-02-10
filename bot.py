from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from getpass import getpass
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


DEFAULT_AUTOMATION_CONFIG: dict[str, object] = {
    "golden_key": "CHANGE_ME",
    "funpay_lots_url": "https://funpay.com/lots/",
    "headless": False,
    "selectors": {
        "lot_card": ".tc-item",
        "edit_button": "a[href*='offerEdit']",
        "title_input": "input[name='title']",
        "description_input": "textarea[name='desc']",
        "submit_button": "button[type='submit']",
    },
}


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


def save_automation_config(destination: Path, payload: dict[str, object]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def load_automation_config(source: Path) -> dict[str, object]:
    return json.loads(source.read_text(encoding="utf-8"))


def ensure_automation_config(path: Path) -> None:
    if path.exists():
        return
    save_automation_config(path, DEFAULT_AUTOMATION_CONFIG)
    print(f"Создан файл конфигурации: {path.resolve()}")
    print("Заполните golden_key и при необходимости обновите CSS-селекторы.")


def configure_golden_key(config_path: Path, config: dict[str, object]) -> dict[str, object]:
    print(f"\nПуть к конфигу: {config_path.resolve()}")
    key = getpass("Введите новый golden_key (пусто = отмена): ").strip()
    if not key:
        print("Настройка отменена.")
        return config

    config["golden_key"] = key
    save_automation_config(config_path, config)
    print("golden_key сохранён в конфиг.")
    return config


def ask_golden_key(config_path: Path, config: dict[str, object]) -> tuple[bool, dict[str, object]]:
    expected = str(config.get("golden_key", ""))
    if not expected or expected == "CHANGE_ME":
        print("В конфиге не задан golden_key.")
        answer = input("Хотите задать его сейчас? (y/n): ").strip().lower()
        if answer in {"y", "yes", "д", "да"}:
            config = configure_golden_key(config_path, config)
            expected = str(config.get("golden_key", ""))
        if not expected or expected == "CHANGE_ME":
            return False, config

    entered = getpass("Введите golden_key: ")
    if entered != expected:
        print("Неверный golden_key. Доступ отклонён.")
        return False, config
    return True, config


def open_funpay_and_edit_lots(config: dict[str, object], rows: list[dict[str, str]]) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as error:
        print("Playwright не установлен. Установите: pip install playwright && playwright install")
        print(f"Детали: {error}")
        return

    url = str(config["funpay_lots_url"])
    selectors = config.get("selectors", {})
    if not isinstance(selectors, dict):
        print("В конфиге selectors должен быть объектом.")
        return

    print("Открываем браузер. Если не авторизованы на FunPay, войдите вручную в открытой вкладке.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=bool(config.get("headless", False)))
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")

        input("Нажмите Enter после того, как страница с лотами полностью готова... ")

        lot_cards = page.locator(str(selectors.get("lot_card", ".tc-item")))
        found = lot_cards.count()
        if found == 0:
            print("Лоты не найдены. Проверьте selectors.lot_card в config.")
            browser.close()
            return

        print(f"Найдено карточек лотов: {found}. Будет обновлено: {min(found, len(rows))}")

        for index, row in enumerate(rows[:found]):
            card = lot_cards.nth(index)
            edit_selector = str(selectors.get("edit_button", "a[href*='offerEdit']"))
            edit_link = card.locator(edit_selector).first
            if edit_link.count() == 0:
                print(f"Карточка {index + 1}: кнопка редактирования не найдена, пропуск.")
                continue

            with page.expect_navigation(wait_until="domcontentloaded"):
                edit_link.click()

            page.fill(str(selectors.get("title_input", "input[name='title']")), row["title"])
            page.fill(
                str(selectors.get("description_input", "textarea[name='desc']")),
                row["description_html"],
            )
            page.click(str(selectors.get("submit_button", "button[type='submit']")))

            print(f"Лот #{index + 1} обновлён: {row['branch']}")
            page.goto(url, wait_until="domcontentloaded")

        print("Готово. Лоты обработаны.")
        browser.close()


def run_console(config_path: Path, csv_path: Path, txt_path: Path) -> None:
    ensure_automation_config(config_path)

    while True:
        config = load_automation_config(config_path)

        print("\n=== FunPay Lot Console ===")
        print("1. Сгенерировать файлы лотов (CSV + TXT)")
        print("2. Редактировать лоты на FunPay (через Playwright)")
        print("3. Настроить golden_key")
        print("4. Показать путь к конфигу")
        print("5. Выход")
        choice = input("Выберите действие (1-5): ").strip()

        if choice == "1":
            rows = build_lot_rows(DEFAULT_LOTS)
            export_to_csv(rows, csv_path)
            export_to_text(rows, txt_path)
            print(f"Сохранено {len(rows)} лотов.")
            print(f"CSV: {csv_path.resolve()}")
            print(f"TXT: {txt_path.resolve()}")
        elif choice == "2":
            ok, config = ask_golden_key(config_path, config)
            if not ok:
                continue
            rows = build_lot_rows(DEFAULT_LOTS)
            open_funpay_and_edit_lots(config, rows)
        elif choice == "3":
            configure_golden_key(config_path, config)
        elif choice == "4":
            print(f"Конфигурация: {config_path.resolve()}")
        elif choice == "5":
            print("Выход.")
            return
        else:
            print("Неизвестный выбор. Введите число от 1 до 5.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Генератор лотов для FunPay по Dota 2 + интерактивная консоль для автозаполнения."
        )
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("output/funpay_dota_lots.csv"),
        help="Путь для CSV-файла",
    )
    parser.add_argument(
        "--txt",
        type=Path,
        default=Path("output/funpay_dota_lots.txt"),
        help="Путь для TXT-файла",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("output/funpay_automation_config.json"),
        help="Путь до JSON-конфига автоматизации",
    )
    parser.add_argument(
        "--mode",
        choices=("generate", "console"),
        default="console",
        help="Режим: generate (только файлы) или console (интерактивное меню)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "generate":
        rows = build_lot_rows(DEFAULT_LOTS)
        export_to_csv(rows, args.csv)
        export_to_text(rows, args.txt)
        print(f"Готово! Создано {len(rows)} лотов.")
        print(f"CSV: {args.csv}")
        print(f"TXT: {args.txt}")
        return

    run_console(args.config, args.csv, args.txt)


if __name__ == "__main__":
    main()
