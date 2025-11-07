import json
import numbers
import os
import threading
import datetime
from typing import Callable, Optional

class UIAccessInterface:
    def __init__(self):
        self._items : dict[str, "UIAccessItem"] = {}

        self._flush_lock = threading.Lock()
        self._subscriber_lock = threading.Lock()
        self._access_lock = threading.Lock()

        self._item_update_subscribers = {}

        self._persist_to_file = False
        self._persist_to_file_path = None

        self._timer = None
        self._last_flush = datetime.datetime.min

    def subscribe_item_update(self, name:str, func:Callable[["UIAccessItem"], None]) -> None:
        with self._subscriber_lock:
            if name not in self._item_update_subscribers:
                self._item_update_subscribers[name] = []
            self._item_update_subscribers[name].append(func)

    def unsubscribe_item_update(self, name:str, func:Callable[["UIAccessItem"], None]) -> None:
        with self._subscriber_lock:
            if name in self._item_update_subscribers:
                functions = self._item_update_subscribers[name]
                if func in functions:
                    functions.remove(func)

    def broadcast_item_update(self, item: "UIAccessItem") -> None:
        self._on_item_update(item)

    def _on_item_update(self, item: "UIAccessItem"):
        funcs = []

        with self._subscriber_lock:
            if item.name in self._item_update_subscribers:
                for func in self._item_update_subscribers[item.name]:
                    funcs.append(func)
            if "*" in self._item_update_subscribers:
                for func in self._item_update_subscribers["*"]:
                    funcs.append(func)

        for func in funcs:
            func(item)

        if self._persist_to_file: self._flush()

    def _register_item(self, item: "UIAccessItem") -> None:
        with self._access_lock:
            self._items[item.name] = item

    def has_item(self, name: str) -> bool:
        with self._access_lock:
            return name in self._items

    def get_item(self, name: str) -> "UIAccessItem":
        with self._access_lock:
            return self._items[name]

    def get_items(self) -> list["UIAccessItem"]:
        with self._access_lock:
            return [value for value in self._items.values()]

    def has_field(self, name:str) -> bool:
        item = self.get_item(name)
        return isinstance(item, UIAccessField)

    def get_field(self, name: str) -> Optional["UIAccessField"]:
        item = self.get_item(name)
        if isinstance(item, UIAccessField):
            return item
        return None

    def get_field_value(self, name: str):
        return self.get_field(name).get()

    def get_field_value_formated(self, name: str):
        return self.get_field(name).get_formatted()

    def has_function(self, name: str) -> bool:
        item = self.get_item(name)
        return isinstance(item, UIAccessFunction)

    def get_function(self, name: str) -> Optional["UIAccessFunction"]:
        item = self.get_item(name)
        if isinstance(item, UIAccessFunction):
            return item
        return None

    def run_function(self, name:str):
        self.get_function(name).run()

    def save_fields(self, filepath: str):
        data = {key: value.serialize() for key, value in self._items.items() if isinstance(value, UIAccessField) and value.can_serialize}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_fields(self, filepath: str, persist_to_file: bool = False):
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            for key, value in data.items():
                if self.has_field(key):
                    field = self.get_field(key)
                    field.override_set(field.deserialize(value))

        self._persist_to_file = persist_to_file
        self._persist_to_file_path = filepath

    def _flush(self):
        if self._persist_to_file and self._persist_to_file_path:
            with self._flush_lock:
                now = datetime.datetime.now()
                time_since_last = now - self._last_flush

                if time_since_last.total_seconds() >= 5:
                    self._do_flush()
                    self._last_flush = now
                else:
                    if self._timer is None or not self._timer.is_alive():
                        delay = 5 - time_since_last.total_seconds()
                        self._timer = threading.Timer(delay, self._scheduled_flush)
                        self._timer.start()

    def _scheduled_flush(self):
        if self._persist_to_file and self._persist_to_file_path:
            with self._flush_lock:
                self._do_flush()
                self._last_flush = datetime.datetime.now()
                self._timer = None  # Reset timer

    def _do_flush(self):
        if self._persist_to_file and self._persist_to_file_path:
            self.save_fields(self._persist_to_file_path)

class UIAccessItem:
    def __init__(self, data_accessor: UIAccessInterface, name: str, title: str = None):
        self._data_accessor = data_accessor
        self._name = name
        self._title = title if title else name

    @property
    def data_accessor(self):
        return self._data_accessor

    @property
    def name(self):
        return self._name

    @property
    def title(self):
        return self._title

class UIAccessField(UIAccessItem):
    def __init__(self, data_accessor: UIAccessInterface, name: str, value, title: str = None, can_set: bool = True,
                 can_serialize: bool = True):
        super().__init__(data_accessor, name, title)
        self._value = value
        self._can_set = can_set
        self._can_serialize = can_serialize

    @property
    def can_set(self):
        return self._can_set

    @property
    def can_serialize(self):
        return self._can_serialize

    def get(self):
        return self._value

    def set(self, value) -> None:
        if self.can_set:
            self.override_set(value)

    def override_set(self, value) -> None:
        self._value = value
        self._data_accessor.broadcast_item_update(self)

    def set_silently(self, value):
        self._value = value

    def format_get(self, value) -> str:
        return str(value)

    def get_formatted(self) -> str:
        return self.format_get(self.get())

    def serialize(self):
        return self.get()

    def deserialize(self, value):
        return value

    def subscribe(self, func:Callable[["UIAccessItem"], None]) -> None:
        self._data_accessor.subscribe_item_update(self._name, func)

    def unsubscribe(self, func:Callable[["UIAccessItem"], None]) -> None:
        self._data_accessor.unsubscribe_item_update(self._name, func)

class UIAccessGraphField(UIAccessField):
    def __init__(self, data_accessor: UIAccessInterface, name: str, value, title: str = None):
        super().__init__(data_accessor, name, value, title, False, False)

class UIAccessNumericField(UIAccessField):
    def __init__(self, data_accessor: UIAccessInterface, name: str, value: float, title: str = None,
                 value_range: tuple[float, float] = None, increment_delta: float = None,
                 on_format: Callable[[object], str] = None, can_set: bool = True, can_serialize: bool = True):
        super().__init__(data_accessor, name, value, title, can_set, can_serialize)
        self._on_format = on_format
        self._value_range = value_range
        self._increment_delta = increment_delta

    @property
    def value_range(self):
        return self._value_range

    @property
    def increment_delta(self):
        return self._increment_delta

    @property
    def has_value_range(self):
        if self._value_range is not None:
            min_val, max_val = self.value_range
            return isinstance(min_val, numbers.Number) and isinstance(max_val, numbers.Number)
        return False

    @property
    def has_increment_delta(self):
        return self._increment_delta is not None and isinstance(self._increment_delta, numbers.Number)

    def set(self, value) -> None:
        super().set(self.clamp(value))

    def clamp(self, value):
        if self.has_value_range:
            min_val, max_val = self.value_range
            if isinstance(value, (int, float)):
                return max(min_val, min(max_val, value))

        return value

    def format_get(self, value) -> str:
        if self._on_format:
            return self._on_format(value)
        else:
            return super().format_get(value)

    def adjust(self, direction: int) -> None:
        if self.can_set and self.has_increment_delta:
            value = self.get()
            if isinstance(value, (int, float)):
                delta = self.increment_delta if direction > 0 else -self.increment_delta
                new_value = value + delta

                self.set(new_value)

class UIAccessFunction(UIAccessItem):
    def __init__(self, data_accessor: UIAccessInterface, name: str,
                 on_run: Callable[["UIAccessFunction"], None] = None, title: str = None,
                 on_check_enabled: Callable[["UIAccessFunction"], bool] = None):
        super().__init__(data_accessor, name, title)
        self._on_run = on_run
        self._on_check_enabled = on_check_enabled

    def is_enabled(self):
        if self._on_check_enabled:
            return self._on_check_enabled(self)
        return True

    def run(self):
        if self._on_run:
            if self.is_enabled():
                self._on_run(self)
                self._data_accessor.broadcast_item_update(self)

class UIAccessListFieldPossibleValue:
    def __init__(self, value, title: str = None):
        self._value = value
        self._title = title

    @property
    def value(self):
        return self._value

    @property
    def title(self):
        return self._title

class UIAccessListField(UIAccessField):
    def __init__(self, data_accessor: UIAccessInterface, name: str, value: list, title: str = None, possible_values: list[UIAccessListFieldPossibleValue] = None, can_set: bool = True,
                 can_serialize: bool = True):
        super().__init__(data_accessor, name, value, title, can_set, can_serialize)

        self._possible_values = possible_values

    @property
    def possible_values(self) -> list[UIAccessListFieldPossibleValue]:
        return self._possible_values

    def has_possible_values(self) -> bool:
        return self._possible_values is not None

    def has_possible_value(self, possible_value: UIAccessListFieldPossibleValue) -> bool:
        get_value = self.get()
        return possible_value.value in get_value

    def toggle_possible_value(self, possible_value: UIAccessListFieldPossibleValue) -> None:
        get_value = self.get()

        if not self.has_possible_value(possible_value):
            self.add_possible_value(possible_value)
        else:
            self.remove_possible_value(possible_value)

    def add_possible_value(self, possible_value: UIAccessListFieldPossibleValue) -> None:
        get_value = self.get()
        get_value.append(possible_value.value)

        self._data_accessor.broadcast_item_update(self)

    def remove_possible_value(self, possible_value: UIAccessListFieldPossibleValue) -> None:
        get_value = self.get()
        get_value.remove(possible_value.value)

        self._data_accessor.broadcast_item_update(self)
