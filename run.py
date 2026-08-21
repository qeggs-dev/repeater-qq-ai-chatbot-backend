from __future__ import annotations
# A lightly dependent Python script launcher!
# Python Simple Launcher For Virtual Environment Scripts
# Sloves Starter !!!

__version__ = "0.5.0"

# region Imports
import re
import os
import sys
import time
import json
import shlex
import ctypes
import atexit
import platform
import traceback
import subprocess
from enum import Enum
from pathlib import Path
from abc import ABC, abstractmethod
from typing import (
    List,
    Dict,
    Tuple,
    Union,
    Optional,
    Any,
    TextIO,
    TypeVar,
    Generic,
    Callable,
    Optional,
    Iterable,
    Generator,
)
# endregion

# region Constants
SYSTEM: str = platform.system()

T_CPV = TypeVar("T_CPV")

class ExitCode(Enum):
    ONLY_PAUSE = -1
    SUCCESS = 0
    CONFIG_NOT_FOUND = 1
    CONFIG_DECODE_ERROR = 2
    CONFIG_ENCODE_ERROR = 3
    CONFIG_WRITE_ERROR = 4
    CONFIG_READ_ERROR = 5
    CONFIG_PERMISSION_ERROR = 6
    SCRIPT_NOT_FOUND = 7
    SCRIPT_NAME_TYPE_ERROR = 8
    SCRIPT_NAME_IS_EMPTY = 9
    SCRIPT_NAME_NOT_PROVIDED = 10
    USER_TERMINATED = 11
    CONFIG_PARSING_ERROR = 12

    UNKNOWN_ERROR = 255
# endregion

# region SetTitle
def set_title(title: str):
    """
    Set console title

    :param title: Title
    """
    if SYSTEM == "Windows":
        try:
            # Win API
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        except Exception:
            subprocess.run(
                ["title", title],
                shell = True,
            )
    else:
        sys.stdout.write(f"\033]2;{title}\007")
        sys.stdout.flush()
# endregion

# center_print
def center_print(text: str, file: TextIO = sys.stdout):
    """
    Center print text

    :param text: Text to print
    """
    file.write(text.center(os.get_terminal_size().columns))
    file.flush()
# endregion

# region IsVenv
def is_venv():
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
# endregion

# region CrossPlatformValue
class CrossPlatformValue(Generic[T_CPV]):
    """Cross-platform value container that returns the corresponding value based on the current operating system."""
    
    def __init__(
        self,
        windows: Optional[T_CPV] = None,
        linux: Optional[T_CPV] = None,
        macos: Optional[T_CPV] = None,
        jvm: Optional[T_CPV] = None,
        default: Optional[T_CPV] = None
    ):
        self._windows_value: Optional[T_CPV] = windows
        self._linux_value: Optional[T_CPV] = linux
        self._macos_value: Optional[T_CPV] = macos
        self._jvm_value: Optional[T_CPV] = jvm
        self._default_value: Optional[T_CPV] = default
    
    @property
    def windows(self) -> Optional[T_CPV]:
        if self._windows_value is not None:
            return self._windows_value
        elif self._default_value is not None:
            return self._default_value
        else:
            raise ValueError("No value provided for the current platform.")
    
    @windows.setter
    def windows(self, value: T_CPV):
        self._windows_value = value
    
    @property
    def linux(self) -> Optional[T_CPV]:
        if self._linux_value is not None:
            return self._linux_value
        elif self._default_value is not None:
            return self._default_value
        else:
            raise ValueError("No value provided for the current platform.")
    
    @linux.setter
    def linux(self, value: T_CPV):
        self._linux_value = value
    
    @property
    def macos(self) -> Optional[T_CPV]:
        if self._macos_value is not None:
            return self._macos_value
        elif self._default_value is not None:
            return self._default_value
        else:
            raise ValueError("No value provided for the current platform.")
    
    @macos.setter
    def macos(self, value: T_CPV):
        self._macos_value = value

    @property
    def jvm(self) -> Optional[T_CPV]:
        if self._jvm_value is not None:
            return self._jvm_value
        elif self._default_value is not None:
            return self._default_value
        else:
            raise ValueError("No value provided for the current platform.")

    @jvm.setter
    def jvm(self, value: T_CPV):
        self._jvm_value = value
    
    @property
    def value(self) -> T_CPV:
        """Get the value corresponding to the current platform."""
        if SYSTEM == "Windows" and self._windows_value is not None:
            return self._windows_value
        elif SYSTEM == "Linux" and self._linux_value is not None:
            return self._linux_value
        elif SYSTEM == "Darwin" and self._macos_value is not None:
            return self._macos_value
        elif SYSTEM == "Java" and self._jvm_value is not None:
            return self._jvm_value
        elif self._default_value is not None:
            return self._default_value
        else:
            raise ValueError("No value provided for the current platform.")
    
    def get_value_or(self, default: T_CPV) -> T_CPV:
        """Get the value, return the provided default value if it is undefined."""
        try:
            return self.value
        except ValueError:
            return default
    
    def is_defined_for_current_platform(self) -> bool:
        """Check if there are defined values in the current platform."""
        if SYSTEM == "Windows":
            return self._windows_value is not None
        elif SYSTEM == "Linux":
            return self._linux_value is not None
        elif SYSTEM == "Darwin":
            return self._macos_value is not None
        elif SYSTEM == "Java":
            return self._jvm_value is not None
        return False
    
    def dump(self) -> Dict[str, T_CPV | None]:
        """Dump the values to a dictionary."""
        return {
            "windows": self.windows,
            "linux": self.linux,
            "macos": self.macos,
            "jvm": self.jvm,
            "default": self._default_value
        }
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return (
            f"CrossPlatformValue("
            f"windows={self._windows_value}, "
            f"linux={self._linux_value}, "
            f"macos={self._macos_value}, "
            f"jvm={self._jvm_value}, "
            f"default={self._default_value}"
            f")"
        )
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CrossPlatformValue):
            return False
        return (self._windows_value == other._windows_value and
                self._linux_value == other._linux_value and
                self._macos_value == other._macos_value and
                self._jvm_value == other._jvm_value and
                self._default_value == other._default_value)
# endregion

# region absolute_path
def absolute_path(path: Union[str, Path], cwd: Optional[Union[str, Path]] = None) -> Path:
    path = Path(path)
    if cwd is None:
        cwd = Path.cwd()
    else:
        cwd = Path(cwd)
    if path.is_absolute():
        return path
    return cwd.resolve() / path
# endregion

# region  Ask
# region > BaseAsk

# The purpose of this base class is to have a uniform base class for all four ASK classes
# To facilitate follow-up to do type judgments
class BaseAsk(ABC):
    """
    Interface for asking questions
    """

    @abstractmethod
    def ask(self) -> Any:
        """
        Asks the user a question and returns the answer
        """
        pass
# endregion

# region >> Ask
T_FILE = TypeVar("T_FILE", bound=TextIO)

class Ask(BaseAsk, Generic[T_FILE]):
    """Ask for user"""
    YES_CHARSET: set[str] = {"y", "yes", "true", "t", "1"}
    NO_CHARSET: set[str] = {"n", "no", "false", "f", "0"}
    def __init__(
            self,
            prompt = "Do you agree?",
            yes_charset: set[str] = YES_CHARSET,
            no_charset: set[str] = NO_CHARSET,
            show_yn_prompt: bool = True,
            default: bool = True,
            file: T_FILE = sys.stdout
        ):
        """
        :param prompt: The prompt to show
        :param yes_charset: The charset of yes answers (must lower case)
        :param no_charset: The charset of no answers (must lower case)
        :param show_yn_prompt: If default is True, show "Y/n" prompt, else "y/N" prompt
        :param default: Default answer  (True = yes, False = no)
        """
        self._prompt = str(prompt)
        self._yes_charset = yes_charset
        self._no_charset = no_charset
        self._show_yn_prompt = show_yn_prompt
        self._default = default
        self._file = file
    
    def ask(self) -> bool:
        self._file.write(self._prompt)
        self._file.write(" ")
        if self._show_yn_prompt:
            self._file.write("[Y/n]" if self._default else "[y/N]")
        self._file.write(": ")
        self._file.flush()
        answer = input().lower()
        if self._default:
            if answer in self._no_charset:
                return False
            else:
                return True
        else:
            if answer in self._yes_charset:
                return True
            else:
                return False

    def __repr__(self):
        return f"Ask[{self._file.__class__.__name__}](\n\t{repr(self._prompt)},\n\tdefault={repr(self._default)},\n\tshow_yn_prompt={repr(self._show_yn_prompt)}\n)"
# endregion

# region > Choose 
T = TypeVar("T")

class Choose(BaseAsk, Generic[T, T_FILE]):
    """Ask the user to choose from a list of values"""
    def __init__(
            self,
            list_name: str,
            list_values: Iterable[T],
            choose_prompt: str = "Choose: ",
            skip_only_one: bool = False,
            file: T_FILE = sys.stdout
        ):
        """
        :param list_name: Name of the list
        :param list_values: List of values
        :param choose_prompt: Prompt for choosing
        """
        self._list_name = str(list_name)
        self._list_values = list(list_values)
        self._choose_prompt = str(choose_prompt)
        self._skip_only_one = bool(skip_only_one)
        self._file: T_FILE = file
    
    def ask(self) -> T:
        if not self._list_values:
            raise ValueError("List is empty")
        
        if self._skip_only_one and len(self._list_values) == 1:
            return self._list_values[0]
        
        self._file.write(self._list_name + "\n")
        for index, value in enumerate(self._list_values, start = 1):
            self._file.write(f"[{index}] {value}\n")
        
        self._file.flush()

        while True:
            choice = input(self._choose_prompt)
            if choice in self._list_values:
                return choice
            else:
                try:
                    choice = int(choice)
                    if choice in range(1, len(self._list_values) + 1):
                        return self._list_values[choice - 1]
                    else:
                        self._file.write("Invalid choice. Please try again.\n")
                        self._file.flush()
                except ValueError:
                    self._file.write("Invalid choice. Please try again.\n")
                    self._file.flush()

    def __str__(self):
        return f"Choose {self._list_name} from {self._list_values}"
    
    def __repr__(self):
        return f"Choose(\n\tlist_name = {repr(self._list_name)},\n\tlist_values = {repr(self._list_values)},\n\tchoose_prompt = {repr(self._choose_prompt)}\n)"
# endregion

# region > FindFile
class FindFile(BaseAsk, Generic[T_FILE]):
    def __init__(
            self,
            base_path: Union[Union[str, Path], Iterable[Union[str, Path]]],
            glob: str = "*",
            excludes: set[Union[str, Path]] = set(),
            recursive_search: bool = False,
            skip_only_one: bool = False,
            file: T_FILE = sys.stdout
        ):
        self._base_path: set[Path] = set()
        if isinstance(base_path, str) or isinstance(base_path, Path):
            self._base_path.add(Path(base_path))
        else:
            for base_path in base_path:
                if isinstance(base_path, str):
                    base_path = Path(base_path)
                self._base_path.add(base_path)
        self._glob = str(glob)
        self._exclude: set = set()
        for base_path in self._base_path:
            for exclude in excludes:
                self._exclude.add(absolute_path(exclude, base_path))
        self._recursive_search = bool(recursive_search)
        self._skip_only_one = bool(skip_only_one)
        self._file = file
    
    @property
    def _file_list(self) -> Generator[Path, None, None]:
        """Get the list of files"""
        path_set: set[Path] = set()
        for path in self._base_path:
            if self._recursive_search:
                generator = path.rglob(self._glob)
            else:
                generator = path.glob(self._glob)
            for path in generator:
                if str(path.resolve()) in path_set:
                    continue
                path_set.add(path.resolve())
                yield path
    
    def ask(self) -> Union[Path, None]:
        """Ask the user to choose a file from the list of files"""
        file_set: set[Path] = set(self._file_list)
        
        if len(file_set) == 0:
            for path in self._base_path:
                self._file.write(f"\"{self._glob}\" No files found in {path}.\n")
            return None
        
        choose = Choose(
            list_name = "Find: ",
            list_values = (file_set - self._exclude),
            choose_prompt = "Choose a file: ",
            skip_only_one = self._skip_only_one,
            file = self._file
        )

        return choose.ask()
    
    def __repr__(self):
        return f"FindFile[{self._file.__class__.__name__}](\n\tbase_path = {repr(self._base_path)},\n\tglob = {repr(self._glob)},\n\trecursive_search = {repr(self._recursive_search)}\n\tskip_only_one = {repr(self._skip_only_one)}\n)"
# endregion
# endregion

# region FormatTimeLevels
TIME_LEVELS: List[Tuple[str, str, int]] = [
    ("nanosecond", "ns", 1000),
    ("microsecond", "μs", 1000),
    ("millisecond", "ms", 1000),
    ("second", "s", 60),
    ("minute", "min", 60),
    ("hour", "h", 24),
    ("day", "day", 30),
    ("month", "mon", 12),
    ("year", "y", 10),
    ("decade", "dec", 10),
    ("century", "cent", 10),
]
# endregion

# region FormatCarryDuration
def format_carry_duration(
    value: int,
    levels: List[Tuple[str, str, int]],
    start_with: int = 0,
    use_abbreviation: bool = False,
    delimiter: str = ", ",
    final_level: Tuple[str, str] = ("max_level", "max"),
    negative_prompt: str = "(Negative) "
) -> str:
    """
    Format a value using a carry system with specified levels.

    Args:
        value (int): The value to format.
        levels (List[Tuple[str, str, int]]): List of (name, abbreviation, divisor) tuples.
        start_with (int, optional): The starting index in levels. Defaults to 0.
        use_abbreviation (bool, optional): Whether to use abbreviations. Defaults to False.
        delimiter (str, optional): Delimiter between units. Defaults to ", ".
        final_level (Tuple[str, str], optional): Final level (name, abbreviation). Defaults to ("max_level", "max").

    Returns:
        str: Formatted value string.
    """
    if not levels:
        raise ValueError("levels cannot be empty")
    
    if start_with not in range(len(levels)):
        raise ValueError(f"start_with must be in range [0, {len(levels)})")
    
    # Handle zero value
    if value == 0:
        name, abbr = levels[0][:2] if levels else ("unit", "unit")
        return f"0 {abbr if use_abbreviation else name}"
    
    # Handle negative value
    is_negative = value < 0
    value = abs(value)
    
    end_level, end_level_abbreviation = final_level
    data_level_stack: List[str] = []
    remaining_part: int = value
    
    # Process each level starting from the specified level
    for name, abbreviation, divisor in levels[start_with:]:
        if remaining_part == 0:
            break
            
        current_value = remaining_part % divisor
        remaining_part //= divisor
        
        if current_value > 0:
            unit = abbreviation if use_abbreviation else name
            # Handle pluralization
            if current_value != 1 and not use_abbreviation:
                unit += "s"
            data_level_stack.append(f"{current_value} {unit}")
        
        if remaining_part == 0:
            break
    
    # Handle the final level
    if remaining_part > 0:
        unit = end_level_abbreviation if use_abbreviation else end_level
        if remaining_part != 1 and not use_abbreviation:
            unit += "s"
        data_level_stack.append(f"{remaining_part} {unit}")
    
    # Reverse the stack to get the correct order (largest to smallest)
    text = delimiter.join(data_level_stack[::-1])
    
    if is_negative:
        text = f"{negative_prompt}{text}"
    
    return text
# endregion

# region MainClass
class SlovesStarter:
    YES_CHARSET: List[str] = ["y", "yes", "true", "t", "1"]
    NO_CHARSET: List[str] = ["n", "no", "false", "f", "0"]
    PIP_FREEZE_REGEX: re.Pattern[str] = re.compile(r"^(?P<name>[\w\d\.\-]+)(==(?P<version>[\w\d\.]+))?$")

    # region > init
    def __init__(self):
        self.python_name: CrossPlatformValue[str] = CrossPlatformValue(
            windows = "python",
            linux = "python3",
            default = "python3"
        )
        self.pip_name: CrossPlatformValue[str] = CrossPlatformValue(
            windows = "pip",
            linux = "pip3",
            default = "pip3"
        )
        self.venv_prompt: str = "venv"
        self.script_name: Optional[Union[str, List[str]]] = None
        self.python_arguments: List[str] = []
        self.arguments: Optional[List[str]] = None
        self.title: str = "Sloves Python Script Starter"
        self.console_title: str = self.title
        self.process_title: str = "Python Script"
        self.process_exit_title: str = self.title
        self.exit_title: str = self.title
        self.use_venv: bool = True
        self.requirements: List[str] = []
        self.requirements_file: CrossPlatformValue[str] = CrossPlatformValue(
            default="requirements.txt"
        )
        self.work_directory: Path = self.cwd
        self.restart:bool = False
        self.reselect: bool = False
        self.run_cmd_need_to_ask: bool = True
        self.ask_default_values: Dict[str, bool] = {}
        self.divider_line_char: str = "="
        self.inject_environment_variables: Dict[str, str] = os.environ.copy()
        self.text_encoding:str = "utf-8"
        self.print_return_code: bool = True
        self.print_runtime: bool = True
        self.automatic_exit: bool = False
        self.allow_print: bool = True

        set_title(self.title)

        try:
            config = self.load_config()
        except FileNotFoundError:
            suffix:int = 0
            while True:
                if suffix == 0:
                    config_file = Path(f"run.json")
                else:
                    config_file = Path(f"run_{suffix}.json")
                
                if not config_file.exists():
                    if self.ask(
                            id = "Create New Configuration File",
                            prompt = "Configuration file not found.\nDo you want to create a new one?",
                            default = True
                        ):
                        self.create_configuration(config_file)
                    break
                else:
                    suffix += 1
            print("Continuing to run the program will operate with the default configuration...")
            self.pause_program(ExitCode.ONLY_PAUSE)
            config = None
        
        try:
            if config:
                self.parse_config(config)
        except Exception as e:
            print(f"Error parsing config: {e}")
            self.pause_program(ExitCode.CONFIG_PARSING_ERROR)
        
        @atexit.register
        def exit_handler():
            """
            This function is called when the program exits.
            """
            set_title(self.exit_title)
            print("Exiting...")
    # endregion
    
    # region > cwd
    @property
    def cwd(self) -> Path:
        """Get the current working directory."""
        return Path.cwd()

    @cwd.setter
    def cwd(self, path: Path):
        """Set the current working directory."""
        os.chdir(path)
    # endregion
    
    # region > load config
    def load_config(self):
        """
        Load the configuration file

        :return: the configuration file
        """
        find_file = FindFile(
            base_path = [Path.cwd(), Path(__file__).parent],
            glob = "*.json",
            skip_only_one = True
        )
        config_file = find_file.ask()
        if config_file is None:
            raise FileNotFoundError("No configuration file found")
        elif config_file.exists():
            try:
                with open(config_file, "r", encoding=self.text_encoding) as file:
                    config = json.load(file)
                    return config
            except json.JSONDecodeError:
                print("Invalid configuration file. Please check the file and try again.")
                self.pause_program(ExitCode.CONFIG_DECODE_ERROR)
            except FileNotFoundError:
                print("Configuration file not found.")
                self.pause_program(ExitCode.CONFIG_NOT_FOUND)
            except PermissionError:
                print("Permission denied. Please check the file permissions and try again.")
                self.pause_program(ExitCode.CONFIG_PERMISSION_ERROR)
            except IOError as e:
                print("An error occurred while reading the configuration file.")
                print(e)
                self.pause_program(ExitCode.UNKNOWN_ERROR)
        else:
            raise FileNotFoundError("Configuration file not found.")
    # endregion
        
    # region > parse config
    def parse_config(self, config: dict) -> None:
        """
        Parses the configuration file and sets the corresponding attributes.

        :param config: The configuration dictionary.
        """
        if not isinstance(config, dict):
            raise TypeError("Config must be a dict")
        def exists_and_is_designated_type(key: str, types: Union[type, Tuple[type, ...]]) -> bool:
            return key in config and isinstance(config[key], types)
        
        def check_all_list_types(data: List[Any], types: Union[type, Tuple[type, ...]]):
            return all(isinstance(item, types) for item in data)
        
        def check_all_dict_types(data: Dict[Any, Any], key_types: Union[type, Tuple[type, ...]], value_types: Union[type, Tuple[type, ...]]):
            return all(isinstance(key, key_types) and isinstance(value, value_types) for key, value in data.items())
        
        if exists_and_is_designated_type("title", str):
            self.title = config["title"]
            self.console_title = self.title
            self.process_title = self.title
            self.process_exit_title = self.title
            self.exit_title = self.title
        
        if exists_and_is_designated_type("console_title", str):
            self.console_title = config["console_title"]
        
        if exists_and_is_designated_type("process_title", str):
            self.process_title = config["process_title"]
            self.process_exit_title = self.process_title
        
        if exists_and_is_designated_type("process_exit_title", str):
            self.process_exit_title = config["process_exit_title"]
        
        if exists_and_is_designated_type("exit_title", str):
            self.exit_title = config["exit_title"]
        
        if exists_and_is_designated_type("python_name", dict):
            data = config["python_name"]
            if check_all_dict_types(data, str, str):
                try:
                    self.python_name = CrossPlatformValue(**data)
                except Exception:
                    pass
        
        if exists_and_is_designated_type("pip_name", dict):
            data = config["pip_name"]
            if check_all_dict_types(data, str, str):
                try:
                    self.pip_name = CrossPlatformValue(**data)
                except Exception:
                    pass
        
        if exists_and_is_designated_type("requirements", list):
            data = config["requirements"]
            if check_all_list_types(data, str):
                self.requirements = data
        
        if exists_and_is_designated_type("requirements_file", dict):
            data = config["requirements_file"]
            if check_all_dict_types(data, str, str):
                try:
                    self.requirements_file = CrossPlatformValue(**data)
                except Exception:
                    pass
        
        if exists_and_is_designated_type("venv_prompt", str):
            self.venv_prompt = config["venv_prompt"]
        
        if exists_and_is_designated_type("script_name", (str, list)) :
            data = config["script_name"]
            if isinstance(data, str):
                self.script_name = data
            elif isinstance(data, list):
                if check_all_list_types(data, str):
                    self.script_name = data
        
        if exists_and_is_designated_type("arguments", list):
            if check_all_list_types(config["arguments"], str):
                self.arguments = config["arguments"]
        
        if exists_and_is_designated_type("python_arguments", list):
            if check_all_list_types(config["python_arguments"], str):
                self.python_arguments = config["python_arguments"]
        
        if exists_and_is_designated_type("use_venv", bool):
            self.use_venv = config["use_venv"]
        
        if exists_and_is_designated_type("cwd", str):
            self.cwd = Path(config["cwd"])
            self.work_directory = self.cwd
        
        if exists_and_is_designated_type("work_directory", str):
            self.work_directory = Path(config["work_directory"])
            
        if exists_and_is_designated_type("restart", bool):
            self.restart = config["restart"]
        
        if exists_and_is_designated_type("reselect", bool):
            self.reselect = config["reselect"]
        
        if exists_and_is_designated_type("run_cmd_need_to_ask", bool):
            self.run_cmd_need_to_ask = config["run_cmd_need_to_ask"]
        
        if exists_and_is_designated_type("ask_default_values", dict):
            if check_all_dict_types(config["ask_default_values"], str, bool):
                self.ask_default_values = config["ask_default_values"]
        
        if exists_and_is_designated_type("divider_line_char", str):
            if len(config["divider_line_char"]) == 1:
                self.divider_line_char = config["divider_line_char"]
        
        if exists_and_is_designated_type("inject_environment_variables", dict):
            if check_all_dict_types(config["inject_environment_variables"], str, str):
                self.inject_environment_variables = config["inject_environment_variables"]
        
        if exists_and_is_designated_type("text_encoding", str):
            self.text_encoding = config["text_encoding"]
        
        if exists_and_is_designated_type("print_return_code", bool):
            self.print_return_code = config["print_return_code"]
        
        if exists_and_is_designated_type("print_runtime", bool):
            self.print_runtime = config["print_runtime"]
        
        if exists_and_is_designated_type("automatic_exit", bool):
            self.automatic_exit = config["automatic_exit"]
        
        if exists_and_is_designated_type("allow_print", bool):
            self.allow_print = config["allow_print"]
    # endregion
    
    # region > create configuration
    def create_configuration(self, output: Optional[Union[str, Path]] = None):
        """
        Creates a configuration file from the current configuration.

        :param output: The output file path.
        :return: Configuration dict
        """
        config = {
            "title": self.title,
            "console_title": self.console_title,
            "process_title": self.process_title,
            "process_exit_title": self.process_exit_title,
            "exit_title": self.exit_title,
            "python_name": self.python_name.dump(),
            "pip_name": self.pip_name.dump(),
            "requirements": self.requirements,
            "requirements_file": self.requirements_file.dump(),
            "cwd": str(self.cwd),
            "work_directory": str(self.work_directory),
            "use_venv": self.use_venv,
            "venv_prompt": self.venv_prompt,
            "script_name": self.script_name,
            "arguments": self.arguments,
            "python_arguments": self.python_arguments,
            "restart": self.restart,
            "reselect": self.reselect,
            "run_cmd_need_to_ask": self.run_cmd_need_to_ask,
            "ask_default_values": self.ask_default_values,
            "divider_line_char": self.divider_line_char,
            "inject_environment_variables": self.inject_environment_variables,
            "text_encoding": self.text_encoding,
            "print_return_code": self.print_return_code,
            "print_runtime": self.print_runtime,
            "automatic_exit": self.automatic_exit,
            "allow_print": self.allow_print,
        }
        if output is None:
            return config
        else:
            with open(output, "w", encoding=self.text_encoding) as f:
                f.write(json.dumps(config, indent=4, ensure_ascii=False))
    # endregion

    # region > pause program
    def pause_program(self, code: Union[ExitCode, int] = ExitCode.SUCCESS, prompt: Optional[str] = None, wait: bool = True):
        """
        Pause the program and wait for user input to continue.

        :param code: The exit code to return when the user presses Ctrl+C.
        :param prompt: The prompt to display to the user.
        :raise SystemExit: If the user presses Ctrl+C and the code is not ExitCode.ONLY_PAUSE.
        """
        if self.allow_print:
            if isinstance(code, ExitCode) and code == ExitCode.ONLY_PAUSE:
                print(prompt or "Press Ctrl+C to continue.")
            else:
                if isinstance(code, ExitCode):
                    print(prompt or f"Press Ctrl+C to Exit with code {code.value}({code.name}).")
                else:
                    print(prompt or f"Press Ctrl+C to Exit with code {code}.")
        if wait:
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                self.exit(code)
        else:
            self.exit(code)
    # endregion

    # region > exit
    def exit(self, code: Optional[Union[ExitCode, int]] = None) -> None:
        if isinstance(code, ExitCode):
            if code == ExitCode.ONLY_PAUSE:
                return
            if self.allow_print:
                print(f"Exit with code {code.value}({code.name}).")
            sys.exit(code.value)
        elif isinstance(code, int):
            if self.allow_print:
                print(f"Exit with code {code}.")
            sys.exit(code)
        else:
            return
    # endregion
    
    # region > run cmd
    def run_cmd(
            self,
            cmd: List[str],
            reason: str,
            cwd: Optional[Path] = None,
            default: bool = True,
            print_return_code: bool = True,
            print_runtime: bool = True,
            runtime_handler: Callable[[int, int], str] = lambda start, end: format_carry_duration(end - start, use_abbreviation=True, levels=TIME_LEVELS, final_level=("millennium", "mill")),
            env: Optional[Dict[str, str]] = None,
            askfile: TextIO = sys.stdout,
            capture_output: bool = False,
            ) -> Union[subprocess.CompletedProcess[bytes], None]:
        """
        Run a command with an interactive prompt to ask the user if they want to continue.

        :param cmd: The command to run.
        :param reason: The reason for running the command.
        :param cwd: The working directory to run the command in.
        :param default: The default value for the prompt.
        :param print_return_code: Whether to print the return code of the command.
        :param env: The environment variables to use when running the command.
        :return: The result of the command. (Return None when the user has not approved.)
        """
        if cwd:
            cwd = absolute_path(cwd)
        if self.allow_print:
            askfile.write(reason + "\n")
            askfile.flush()
        run = self.ask(
            id = "Run Cmd",
            prompt = f"Running:\n{shlex.join(cmd)}\nwith cwd: \"{cwd}\"\nRun this command?",
            default = default,
            askfile = askfile
        )
        
        if run:
            if not cmd:
                askfile.write("Warning: No command to run\n")
                askfile.flush()
                return None
            try:
                if self.allow_print:
                    self.print_divider_line()
                start = time.perf_counter_ns()
                result: subprocess.CompletedProcess[bytes] = subprocess.run(
                    cmd,
                    cwd = cwd,
                    env = env,
                    capture_output = capture_output
                )
                if self.allow_print:
                    self.print_divider_line()
                if print_return_code:
                    askfile.write(f"Command returned with code {result.returncode}\n")
                    askfile.flush()
                return result
            except FileNotFoundError as e:
                if self.allow_print:
                    self.print_divider_line()
                askfile.write(f"Error: Command not found: {e}\n")
                askfile.flush()
                raise
            except Exception as e:
                if self.allow_print:
                    self.print_divider_line()
                askfile.write(f"Error running command: {e}\n")
                askfile.flush()
                raise
            finally:
                end = time.perf_counter_ns()
                if print_runtime and callable(runtime_handler):
                    askfile.write(runtime_handler(start, end))
                    askfile.write("\n")
                    askfile.flush()
        else:
            return None
    # endregion
    
    # region > ask
    def ask(
            self,
            id: str,
            prompt: str,
            default: bool = True,
            askfile: TextIO = sys.stdout
        ) -> bool:
        """
        Ask the user a question

        :param prompt: The question to ask
        :param default: The default answer
        :param askfile: The file to ask the question to
        :return: The user's answer
        """
        def automatic_skip_prompt_print():
            askfile.write(str(prompt))
            if default:
                askfile.write(" [Y/n] ")
                askfile.write("y")
            else:
                askfile.write(" [y/N] ")
                askfile.write("n")
            askfile.flush()
        
        if self.run_cmd_need_to_ask:
            if id in self.ask_default_values:
                automatic_skip_prompt_print()
                return self.ask_default_values[id]
            elif prompt in self.ask_default_values:
                automatic_skip_prompt_print()
                return self.ask_default_values[prompt]
            else:
                return Ask(prompt, default=default, file=askfile).ask()
        else:
            return default
    # endregion

    # region > Virtual environment path
    @property
    def venv_bin_path(self):
        if SYSTEM == "Windows":
            return self.work_directory / ".venv" / "Scripts"
        else:
            return self.work_directory / ".venv" / "bin"
    # endregion

    # region > Initialize virtual environment
    def init_venv(self, ignore_existing: bool = True, askfile: TextIO = sys.stdout):
        """
        Initialize virtual environment

        :param ignore_existing: Ignore existing virtual environment
        """
        if not (ignore_existing and (self.work_directory / ".venv" / "pyvenv.cfg").exists()):
            self.print_divider_line()
            if self.run_cmd(
                    [self.python_name.value, "-m", "venv", ".venv", "--prompt", self.venv_prompt],
                    reason = "Initializing virtual environment",
                    cwd = self.work_directory,
                    print_return_code = self.print_return_code,
                    print_runtime = self.print_runtime,
                ) is not None:
                if not (self.work_directory / self.requirements_file.value).exists():
                    if self.ask(id = "Create requirements file", prompt="Create a requirements.txt file", default=True, askfile=askfile):
                        with open(self.work_directory / self.requirements_file.value, "w", encoding=self.text_encoding) as f:
                            for package in self.requirements:
                                f.write(f"{package}\n")
                if (self.work_directory / self.requirements_file.value).exists():
                    if self.run_cmd(
                            [str(self.venv_bin_path / self.pip_name.value), "install", "-r", self.requirements_file.value],
                            reason="Installing requirements",
                            cwd=self.work_directory,
                            print_return_code = self.print_return_code and not self.allow_print,
                            print_runtime = self.print_runtime and not self.allow_print,
                        ) is None:
                        print("Error: Failed to install requirements.")
                
            else:
                print("Error: Failed to initialize virtual environment.")
    # endregion
    
    # region > Run the program
    def get_start_cmd(self, askfile: TextIO = sys.stdout):
        """
        Get the command to start the program

        :return: The command to start the program
        """
        script_name = self.script_name
        
        if self.script_name is None:
            suspected_script_file:List[Path] = []
            self_path = Path(sys.argv[0])
            for file in self.work_directory.glob("*.py"):
                if file != self_path:
                    suspected_script_file.append(file)
            if len(suspected_script_file) == 0:
                print("Error: No Python script files found in the current directory.")
                self.pause_program(ExitCode.SCRIPT_NOT_FOUND)
            find_file = FindFile(
                self.work_directory,
                "*.py",
                excludes={sys.argv[0]},
                skip_only_one=True,
                file = askfile,
            )
            asked = find_file.ask()
            if asked is None:
                self.pause_program(ExitCode.SCRIPT_NOT_FOUND)
                
            script_name = absolute_path(asked, self.work_directory)
        elif isinstance(self.script_name, list):
            choose = Choose(
                "Python script file",
                self.script_name,
                choose_prompt="Choose a Python script file",
                skip_only_one=True,
                file = askfile,
            )
            script_name = absolute_path(choose.ask(), self.work_directory)
        elif isinstance(self.script_name, str) or isinstance(self.script_name, Path):
            if absolute_path(self.script_name, self.work_directory).exists():
                script_name = absolute_path(self.script_name, self.work_directory)
            else:
                print("Error: Script not found!")
                self.pause_program(ExitCode.SCRIPT_NOT_FOUND)
        else:
            print("`script_name` must be a string or a list/tuple of strings")
            self.pause_program(ExitCode.SCRIPT_NAME_TYPE_ERROR)
        
        if script_name is None:
            print("Error: No script name provided")
            self.pause_program(ExitCode.SCRIPT_NAME_NOT_PROVIDED)
        
        if not Path(script_name).exists():
            print(f"Error: Script \"{script_name}\" is not existing")
        
        if self.use_venv:
            if SYSTEM == "Windows":
                start = [str(self.work_directory / ".venv" / "Scripts" / self.python_name.value), *self.python_arguments, str(script_name)]
            else:
                start = [str(self.work_directory / ".venv" / "bin" / self.python_name.value), *self.python_arguments, str(script_name)]
        else:
            start = [self.python_name.value, *self.python_arguments, str(script_name)]

        if self.arguments:
            start.extend(self.arguments)
            if self.allow_print:
                print("Use argument:")
                print(shlex.join(self.arguments))
        else:
            if len(sys.argv) > 1:
                argument = sys.argv[1:]
                if self.allow_print:
                    print("Use argument:")
                    print(shlex.join(argument))
                start.extend(argument)
        return start
    # endregion

    # region > print_divider_line
    def print_divider_line(self, char: Optional[str] = None):
        """
        Print divider line

        :param char: Divider Char
        """
        print((char or self.divider_line_char) * os.get_terminal_size().columns)
    # endregion

    # region > main
    def main(self):
        """
        Main function
        """
        if self.allow_print:
            center_print(self.console_title)
            self.print_divider_line()
        if is_venv() and self.allow_print:
            print("Starter Run in Virtual Environment")
        set_title(self.title)
        if self.use_venv:
            self.init_venv()
        if self.allow_print:
            print(f"Run With Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return_code = ExitCode.SUCCESS
        first_run = True
        reselect = self.reselect
        while True:
            try:
                if reselect or first_run:
                    start = self.get_start_cmd()
                set_title(self.process_title)
                result = self.run_cmd(
                    start,
                    reason = "Running the program",
                    cwd = self.work_directory,
                    env = self.inject_environment_variables,
                    print_return_code = self.print_return_code and self.allow_print,
                    print_runtime = self.print_runtime and self.allow_print,
                )
                if result is not None:
                    if result.returncode != 0:
                        print("An error occurred while running the program.")
                        return_code = result.returncode
            except KeyboardInterrupt:
                    print("Program terminated by user.")
            except Exception as e:
                print(f"An error occurred while running the program.\nError: {e}")
            finally:
                # Reset Title
                first_run = False
                set_title(self.process_exit_title)
            
            if self.restart:
                if self.reselect:
                    ask = Ask("Re-select?")
                else:
                    ask = Ask("Restart?")
                
                if ask.ask():
                    if self.reselect:
                        reselect = True
                    else:
                        reselect = False
                else:
                    break
            else:
                break
        
        if self.automatic_exit:
            self.exit(return_code)
        else:
            self.pause_program(return_code)
    # endregion
# endregion

# region Start
if __name__ == "__main__":
    # This is supposed to be read from the inside
    # However, it is possible to have undefined variables here
    # So we've chosen to use the method of external variable + internal value override
    text_encoding = "utf-8"
    try:
        starter = SlovesStarter()
        text_coding = starter.text_encoding
        starter.main()
    except KeyboardInterrupt:
        print("Program terminated by user.")
        sys.exit(ExitCode.USER_TERMINATED.value)
    except Exception as e:
        with open("Traceback.txt", "w", encoding=text_encoding) as f:
            f.write(traceback.format_exc())
        traceback.print_exc()
        sys.exit(ExitCode.UNKNOWN_ERROR.value)
# endregion